#!/usr/bin/env python3
"""Prepare alpha-only border geometry candidates for the 2026-09-17 backlog.

This script never replaces a master or delivery image. It requires the audited
paper mask for each unchanged source and writes reviewable candidates/reports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from border_geometry import cutout, keep_components, disk

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "revisions/border-alpha-20260917"
QA = ROOT / "qa/border-alpha-20260917"


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def process(aid, audit):
    source = ROOT / f"masters/{aid}.png"
    audited = audit[aid]
    if sha(source) != audited["source_sha256"]:
        raise ValueError("Source differs from audited master")
    paper_path = ROOT / audited["candidate"]
    if sha(paper_path) != audited["candidate_sha256"]:
        raise ValueError("Audited paper input changed")
    raw = np.asarray(Image.open(source).convert("RGB")).copy()
    paper = np.asarray(Image.open(paper_path).convert("RGBA"))[:, :, 3] >= 128
    if paper.shape != raw.shape[:2]:
        raise ValueError("Paper mask dimensions differ")
    low = raw.min(axis=2)
    chroma = raw.max(axis=2).astype(np.int16) - low.astype(np.int16)
    core = keep_components((chroma > 18) & paper, 100)
    if not core.any():
        raise ValueError("No colored core")
    painted = ndi.binary_fill_holes(core)
    # Open only existing, sizeable holes in the audited alpha mask. Any other
    # openings remain a visual-review issue rather than a speculative cut.
    complement, n = ndi.label(~paper)
    exterior = set(np.unique(np.r_[complement[0], complement[-1], complement[:, 0], complement[:, -1]]))
    counts = np.bincount(complement.ravel(), minlength=n + 1)
    hole_labels = [i for i in range(1, n + 1) if i not in exterior and counts[i] >= 100]
    seeds = []
    for label in hole_labels:
        coords = np.argwhere(complement == label)
        for y, x in coords:
            if not core[y, x]:
                seeds.append((int(x), int(y)))
                break
    # The production contour is spline based. Euclidean EDT is sufficient to
    # estimate the preexisting paper width before that single expensive fit.
    distance = ndi.distance_transform_edt(~painted)
    edge = paper & ~ndi.binary_erosion(paper)
    widths = distance[edge]
    widths = widths[(widths > 8) & (widths < 70)]
    if len(widths) < 100:
        raise ValueError("Cannot measure paper width")
    measured = float(np.median(widths))
    # Some paper borders contain deliberate gray shading. Such pixels should
    # not force the margin down to a few pixels; check the final edge instead.
    start_radius = round(float(np.quantile(widths, .05)) - 1.2, 1)
    if start_radius <= 8 or start_radius <= measured * .6:
        raise ValueError(f"Unsafe paper radius {start_radius} from measured {measured:.2f}")
    for attempt in range(9):
        radius = round(start_radius - .8 * attempt, 1)
        if radius <= 7 or radius <= measured * .55:
            raise ValueError("No safe geometric inset within existing paper")
        rgba, protected, distances, geometry = cutout(raw, paper, radius, seeds)
        alpha = rgba[:, :, 3]
        if not np.any((alpha > 0) & ~paper):
            break
    else:
        raise ValueError("Cutout extends beyond audited paper mask")
    rgba[:, :, :3] = raw
    if np.any(alpha[protected] != 255):
        raise ValueError("Protected paint not opaque")
    partial = (alpha > 0) & (alpha < 255)
    # RGB at the antialiased edge should be pale paper, not printed background.
    edge_colored = int(np.count_nonzero(partial & ((low < 230) | (chroma > 18))))
    destination = OUT / f"{aid}.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise ValueError("Candidate exists; refusing overwrite")
    Image.fromarray(rgba, "RGBA").save(destination)
    check = np.asarray(Image.open(destination).convert("RGBA"))
    assert np.array_equal(check[:, :, :3], raw)
    assert check.shape == (raw.shape[0], raw.shape[1], 4)
    report = dict(
        id=aid, created_utc=datetime.now(timezone.utc).isoformat(),
        source=f"masters/{aid}.png", source_sha256=sha(source),
        paper_input=audited["candidate"], paper_input_sha256=sha(paper_path),
        candidate=destination.relative_to(ROOT).as_posix(), candidate_sha256=sha(destination),
        method="border_geometry.cutout, measured inset, original RGB restored",
        dimensions=[raw.shape[1], raw.shape[0]], dimensions_unchanged=True,
        rgb_changed_pixels=0, measured_paper_width_px=measured, radius_px=radius,
        paper_holes=len(hole_labels), hole_seeds=seeds,
        visible_pixels_outside_paper=0, partial_alpha_edge_colored_pixels=edge_colored,
        transparent_pixels=int(np.count_nonzero(alpha == 0)),
        partial_alpha_pixels=int(np.count_nonzero(partial)),
        corner_alpha=[int(alpha[0, 0]), int(alpha[0, -1]), int(alpha[-1, 0]), int(alpha[-1, -1])],
        geometry=geometry, status="pending_visual_review",
    )
    write_json(QA / f"{aid}.json", report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", nargs="*")
    parser.add_argument("--all-needs-alpha", action="store_true")
    args = parser.parse_args()
    progress = json.loads((ROOT / "state/progress.json").read_text(encoding="utf-8"))
    ids = [a["id"] for a in progress["assets"] if a["status"] == "needs_alpha"] if args.all_needs_alpha else args.ids
    audit = {a["id"]: a for a in json.loads((ROOT / "qa/alpha-audit-20260916/audit.json").read_text(encoding="utf-8"))}
    results = []
    for aid in ids:
        try:
            path = QA / f"{aid}.json"
            result = json.loads(path.read_text(encoding="utf-8")) if path.exists() else process(aid, audit)
            print(f"OK {aid} radius={result['radius_px']} edge_colored={result['partial_alpha_edge_colored_pixels']}", flush=True)
        except Exception as error:
            result = {"id": aid, "status": "needs_manual_review", "error": str(error)}
            print(f"REVIEW {aid}: {error}", flush=True)
        results.append(result)
        write_json(QA / "batch.json", results)


if __name__ == "__main__":
    main()
