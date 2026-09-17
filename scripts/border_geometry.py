"""Pure geometry helpers for a reviewed white-paper border restoration trial.

This module does not read or write files. ``cutout`` preserves the canvas and
the protected artwork RGB, but may restore RGB in the surrounding white paper.
It is therefore a border-restoration method, not an alpha-only operation.
Hole seeds use integer pixel indices (x, y). Contours use pixel-square corners,
so the geometric centre of pixel (x, y) is (x + .5, y + .5).
"""

from __future__ import annotations

import warnings

import numpy as np
from scipy import ndimage
from scipy.interpolate import splprep, splev
from scipy.spatial import cKDTree


def disk(radius: float) -> np.ndarray:
    """Return a centred Euclidean disk suitable for binary morphology."""
    if not np.isfinite(radius) or radius < 0:
        raise ValueError("Disk radius must be finite and nonnegative")
    extent = int(np.ceil(radius))
    y, x = np.ogrid[-extent : extent + 1, -extent : extent + 1]
    return x * x + y * y <= radius * radius


def keep_components(mask: np.ndarray, minimum_size: int = 100) -> np.ndarray:
    """Keep 4-connected foreground components meeting ``minimum_size``."""
    mask = np.asarray(mask, dtype=bool)
    if mask.ndim != 2 or minimum_size < 1:
        raise ValueError("Expected a 2D mask and positive minimum_size")
    labels, count = ndimage.label(mask)
    sizes = np.bincount(labels.ravel(), minlength=count + 1)
    keep = sizes >= minimum_size
    keep[0] = False
    return keep[labels]


def summarize(values: np.ndarray) -> dict:
    """Return compact, JSON-compatible statistics for finite numeric values."""
    values = np.asarray(values).ravel()
    values = values[np.isfinite(values)]
    if not values.size:
        return {"count": 0}
    quantiles = np.quantile(values, [0.05, 0.25, 0.5, 0.75, 0.95])
    return {
        "count": int(values.size),
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
        "p05": float(quantiles[0]),
        "p25": float(quantiles[1]),
        "median": float(quantiles[2]),
        "p75": float(quantiles[3]),
        "p95": float(quantiles[4]),
    }


def contour_points(mask: np.ndarray) -> list[np.ndarray]:
    """Trace ordered, closed pixel-square edges, including hole contours.

    Pixel (x, y) occupies [x, x+1] by [y, y+1]. Every returned contour
    repeats its first vertex at the end. Ambiguous diagonal contacts raise
    an assertion instead of silently changing the reviewed traversal.
    """
    mask = np.asarray(mask, dtype=bool)
    if mask.ndim != 2:
        raise ValueError("Expected a 2D mask")
    padded = np.pad(mask, 1, constant_values=False)
    neighbours = (
        padded[:-2, 1:-1],
        padded[1:-1, 2:],
        padded[2:, 1:-1],
        padded[1:-1, :-2],
    )
    offsets = (((0, 0), (1, 0)), ((1, 0), (1, 1)),
               ((1, 1), (0, 1)), ((0, 1), (0, 0)))
    edges: dict[tuple[int, int], tuple[int, int]] = {}
    for neighbour, (start_offset, end_offset) in zip(neighbours, offsets):
        ys, xs = np.nonzero(mask & ~neighbour)
        for x, y in zip(xs.tolist(), ys.tolist()):
            start = (x + start_offset[0], y + start_offset[1])
            end = (x + end_offset[0], y + end_offset[1])
            assert start not in edges, "Ambiguous diagonal contact in painted contour"
            edges[start] = end
    contours = []
    while edges:
        first = next(iter(edges))
        vertices = [first]
        current = edges.pop(first)
        while current != first:
            vertices.append(current)
            current = edges.pop(current)
        vertices.append(first)
        contours.append(np.asarray(vertices, dtype=np.float64))
    return contours


def _dense_splines(contours: list[np.ndarray], target_rms: float = 0.6):
    """Fit periodic boundaries and sample four times per input vertex."""
    dense, records = [], []
    for contour in contours:
        unique_count = len(contour) - 1
        if unique_count < 4:
            raise ValueError("A closed contour needs at least four unique vertices")
        smoothing = len(contour) * target_rms * target_rms
        # FITPACK reports some convergence problems as warnings. Fail rather
        # than silently substituting a different method on a production trial.
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            spline, parameters = splprep(contour.T, per=True, s=smoothing, k=3)
        fitted = np.column_stack(splev(parameters, spline))
        rms = float(np.sqrt(np.mean(np.sum((fitted - contour) ** 2, axis=1))))
        count = len(contour) * 4
        points = np.column_stack(splev(np.linspace(0, 1, count, endpoint=False), spline))
        dense.append(points)
        records.append({"vertices": unique_count, "samples": int(len(points)),
                        "fit_rms_px": rms, "target_rms_px": target_rms,
                        "largest_sample_step_px": float(np.linalg.norm(
                            np.roll(points, -1, axis=0) - points, axis=1).max())})
    return np.concatenate(dense), records


def cutout(rgb: np.ndarray, paper_mask: np.ndarray, radius: float,
           hole_seeds=(), core_mask=None):
    """Restore an offset white-paper margin around the coloured artwork.

    Parameters
    ----------
    rgb : uint8 array, H x W x 3
        Original RGB artwork. The caller must supply the original image.
    paper_mask : boolean array, H x W
        The whole existing sticker silhouette, including its white paper.
        This limits core detection and white samples, not the new offset edge.
    radius : float
        White margin's target distance from the fitted painted boundary.
    hole_seeds : sequence of (x, y)
        Optional seeds inside enclosed openings in the coloured core. Seeds
        connected to canvas exterior raise an error instead of deleting art.

    Returns ``(rgba, protected, distances, report)``. Distances are the original
    nonnegative spline distances. A sigma-3 smoothed field controls alpha.
    The painted mask is fully opaque; only its complement receives coverage.
    No input array is modified. Canvas size and protected RGB are asserted.
    """
    rgb = np.asarray(rgb)
    paper_mask = np.asarray(paper_mask, dtype=bool)
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("rgb must be an H x W x 3 uint8 array")
    if paper_mask.shape != rgb.shape[:2]:
        raise ValueError("paper_mask shape must match the RGB canvas")
    if not np.isfinite(radius) or radius <= 4:
        raise ValueError("radius must be finite and greater than protected radius 4")
    height, width = paper_mask.shape
    low = rgb.min(axis=2)
    chroma = rgb.max(axis=2).astype(np.int16) - low.astype(np.int16)
    core = keep_components((chroma > 18) & paper_mask, 100) if core_mask is None else keep_components(np.asarray(core_mask, dtype=bool) & paper_mask, 100)
    if not core.any():
        raise ValueError("No coloured artwork component of at least 100 pixels")
    painted = ndimage.binary_fill_holes(core)
    holes = []
    seeds = tuple(hole_seeds)
    if seeds:
        complement, _ = ndimage.label(~core)
        exterior_labels = np.unique(np.concatenate((complement[0], complement[-1],
                                                    complement[:, 0], complement[:, -1])))
        for seed in seeds:
            if len(seed) != 2:
                raise ValueError("Hole seed must contain (x, y)")
            x, y = map(int, seed)
            if (x, y) != tuple(seed) or not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"Hole seed {seed!r} is not an in-canvas integer pixel")
            label = int(complement[y, x])
            if label == 0:
                raise ValueError(f"Hole seed {(x, y)} lies in the painted core")
            if label in exterior_labels:
                raise ValueError(f"Hole seed {(x, y)} connects to canvas exterior")
            hole = complement == label
            painted[hole] = False
            holes.append({"seed": [x, y], "pixels": int(hole.sum())})
    protected = ndimage.binary_dilation(painted, structure=disk(4))
    contours = contour_points(painted)
    points, fits = _dense_splines(contours)
    tree = cKDTree(points)
    yy, xx = np.indices((height, width))
    coordinates = np.column_stack((xx.ravel() + 0.5, yy.ravel() + 0.5))
    distances = tree.query(coordinates, workers=4)[0].reshape(height, width)
    field = ndimage.gaussian_filter(distances, sigma=3)
    alpha = np.uint8(painted | (field <= radius)) * 255
    near = ~painted & (np.abs(field - radius) <= 0.8)
    rows, cols = np.nonzero(near)
    coverage = np.zeros(len(rows), dtype=np.float64)
    offsets = (np.arange(8) + 0.5) / 8
    for dy in offsets:
        for dx in offsets:
            sampled = ndimage.map_coordinates(field, [rows + dy - 0.5, cols + dx - 0.5],
                                              order=1)
            coverage += sampled <= radius
    alpha[rows, cols] = np.uint8(np.rint(coverage * 255 / 64))
    if not np.all(alpha[protected] == 255):
        raise ValueError("Offset contour would cut into protected artwork; review geometry")

    safe_white = (low >= 245) & (chroma <= 8) & paper_mask & ~protected
    if not safe_white.any():
        raise ValueError("No safe white paper pixels available for border restoration")
    nearest = ndimage.distance_transform_edt(~safe_white, return_distances=False,
                                           return_indices=True)
    white = rgb[nearest[0], nearest[1]].astype(np.float64)
    white = ndimage.gaussian_filter(white, sigma=(2, 2, 0))
    repairable = ~protected & (distances <= radius + 3)
    weight = np.clip((distances - (radius - 12)) / 4, 0, 1)
    dirty = (low < 245) & (chroma <= 18) & repairable
    weight[dirty] = 1
    weight[~repairable] = 0
    restored = np.rint(rgb.astype(np.float64) * (1 - weight[..., None])
                       + white * weight[..., None]).clip(0, 255).astype(np.uint8)
    restored[protected] = rgb[protected]
    rgba = np.dstack((restored, alpha))
    changed = np.any(restored != rgb, axis=2)
    assert rgba.shape == (height, width, 4)
    assert np.array_equal(rgba[..., :3][protected], rgb[protected])
    assert not np.any(changed & ~repairable)
    partial = (alpha > 0) & (alpha < 255)
    report = {
        "method": "pixel-square spline contour with Euclidean offset white margin",
        "dimensions": [width, height],
        "dimensions_unchanged": True,
        "rgb_protected_unchanged": True,
        "rgb_changed_pixels": int(changed.sum()),
        "rgb_changed_chromatic_pixels": int((changed & (chroma > 18)).sum()),
        "rgb_changed_outside_paper": int((changed & ~paper_mask).sum()),
        "painted_pixels": int(painted.sum()),
        "protected_pixels": int(protected.sum()),
        "safe_white_pixels": int(safe_white.sum()),
        "dirty_white_pixels": int(dirty.sum()),
        "radius_px": float(radius),
        "protected_radius_px": 4,
        "distance_gaussian_sigma_px": 3,
        "alpha_samples_per_pixel": 64,
        "transparent_pixels": int((alpha == 0).sum()),
        "partial_alpha_pixels": int(partial.sum()),
        "visible_pixels_outside_paper": int(((alpha > 0) & ~paper_mask).sum()),
        "opaque_pixels_outside_paper": int(((alpha == 255) & ~paper_mask).sum()),
        "border_distance_at_partial_alpha": summarize(distances[partial]),
        "smoothed_distance_at_partial_alpha": summarize(field[partial]),
        "holes": holes,
        "contour_fits": fits,
        "status": "trial_requires_visual_review",
    }
    return rgba, protected, distances, report
