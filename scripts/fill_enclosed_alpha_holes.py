#!/usr/bin/env python3
"""Fill opaque debris inside already-transparent enclosed openings.

The operation changes alpha only. RGB bytes and canvas dimensions are invariant.
For each sufficiently large transparent component that does not touch the canvas
edge, every horizontal span between that component's leftmost and rightmost
transparent pixel is made transparent. This removes small opaque islands while
preserving the component's existing outer geometry.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def components(mask):
    height, width = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    for start_y in range(height):
        for start_x in range(width):
            if seen[start_y, start_x] or not mask[start_y, start_x]:
                continue
            stack = [(start_x, start_y)]
            seen[start_y, start_x] = True
            pixels = []
            while stack:
                x, y = stack.pop()
                pixels.append((x, y))
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((nx, ny))
            yield pixels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--threshold", type=int, default=64)
    parser.add_argument("--min-area", type=int, default=10)
    parser.add_argument(
        "--box",
        action="append",
        default=[],
        help="Optional alpha-clear box x1,y1,x2,y2; may be repeated.",
    )
    args = parser.parse_args()

    source = Path(args.source)
    destination = Path(args.destination)
    rgba = np.asarray(Image.open(source).convert("RGBA")).copy()
    original_rgb = rgba[:, :, :3].copy()
    original_size = (rgba.shape[1], rgba.shape[0])
    alpha = rgba[:, :, 3]
    height, width = alpha.shape
    changed = 0
    cleaned = []

    for pixels in components(alpha < args.threshold):
        if len(pixels) < args.min_area:
            continue
        xs = [point[0] for point in pixels]
        ys = [point[1] for point in pixels]
        if min(xs) == 0 or min(ys) == 0 or max(xs) == width - 1 or max(ys) == height - 1:
            continue
        rows = {}
        for x, y in pixels:
            rows.setdefault(y, []).append(x)
        before = int(np.count_nonzero(alpha))
        for y, row_xs in rows.items():
            alpha[y, min(row_xs) : max(row_xs) + 1] = 0
        delta = before - int(np.count_nonzero(alpha))
        if delta:
            changed += delta
            cleaned.append({"area": len(pixels), "bbox": [min(xs), min(ys), max(xs) + 1, max(ys) + 1], "cleared": delta})

    cleared_boxes = []
    for raw_box in args.box:
        x1, y1, x2, y2 = (int(value) for value in raw_box.split(","))
        if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
            raise ValueError(f"Unsafe box: {raw_box}")
        before = int(np.count_nonzero(alpha[y1:y2, x1:x2]))
        alpha[y1:y2, x1:x2] = 0
        changed += before
        cleared_boxes.append({"bbox": [x1, y1, x2, y2], "cleared": before})

    rgba[:, :, 3] = alpha
    destination.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(destination)
    check = np.asarray(Image.open(destination).convert("RGBA"))
    assert (check.shape[1], check.shape[0]) == original_size
    assert np.array_equal(check[:, :, :3], original_rgb)
    print(json.dumps({
        "source": source.as_posix(),
        "destination": destination.as_posix(),
        "dimensions": list(original_size),
        "rgb_unchanged": True,
        "alpha_only": True,
        "cleared_pixels": changed,
        "components": cleaned,
        "boxes": cleared_boxes,
    }, indent=2))


if __name__ == "__main__":
    main()
