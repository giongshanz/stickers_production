#!/usr/bin/env python3
"""Review candidates for four silhouettes the default chroma core cannot fit."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from border_geometry import cutout, disk, keep_components

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "revisions/border-alpha-20260917-exceptions"
QA = ROOT / "qa/border-alpha-20260917/exceptions"
IDS = ("stage-spotlight", "foraging-knife", "panda-plant-pot", "wild-garlic-bundle")


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main():
    audit = {r["id"]: r for r in json.loads((ROOT / "qa/alpha-audit-20260916/audit.json").read_text(encoding="utf-8"))}
    OUT.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    for aid in IDS:
        try:
            src = ROOT / f"masters/{aid}.png"
            row = audit[aid]
            if sha(src) != row["source_sha256"]:
                raise ValueError("Source master changed")
            rgb = np.asarray(Image.open(src).convert("RGB")).copy()
            low = rgb.min(axis=2)
            chroma = rgb.max(axis=2).astype(np.int16) - low.astype(np.int16)
            if aid == "wild-garlic-bundle":
                core = keep_components(chroma > 14, 100)
                core = ndi.binary_closing(core, structure=disk(1))
                paper = ndi.binary_dilation(ndi.binary_fill_holes(core), structure=disk(27))
                radius = 16.0
                paper_input = "derived from chromatic artwork; audited mask omitted the object"
            else:
                paper_path = ROOT / row["candidate"]
                paper = np.asarray(Image.open(paper_path).convert("RGBA"))[:, :, 3] >= 128
                core = keep_components(((chroma > 18) | (low < 205)) & paper, 100)
                core = ndi.binary_closing(core, structure=disk(1))
                painted = ndi.binary_fill_holes(core)
                distance = ndi.distance_transform_edt(~painted)
                edge = paper & ~ndi.binary_erosion(paper)
                widths = distance[edge]
                widths = widths[(widths > 7) & (widths < 70)]
                if len(widths) < 100:
                    raise ValueError("Cannot measure paper")
                radius = float(np.round(np.quantile(widths, .05) - 1.2, 1))
                paper_input = row["candidate"]
            for attempt in range(12):
                trial_radius = round(radius - attempt * .8, 1)
                if trial_radius <= 7:
                    raise ValueError("Cannot find safe margin")
                rgba, protected, _, geometry = cutout(rgb, paper, trial_radius, core_mask=core)
                if not np.any((rgba[:, :, 3] > 0) & ~paper):
                    break
            else:
                raise ValueError("New border exceeds paper")
            rgba[:, :, :3] = rgb
            alpha = rgba[:, :, 3]
            partial = (alpha > 0) & (alpha < 255)
            edge_colored = int(np.count_nonzero(partial & ((low < 230) | (chroma > 18))))
            dst = OUT / f"{aid}.png"
            if dst.exists():
                raise ValueError("Candidate already exists")
            Image.fromarray(rgba, "RGBA").save(dst)
            report = dict(id=aid, source=f"masters/{aid}.png", source_sha256=sha(src),
                          paper_input=paper_input, candidate=dst.relative_to(ROOT).as_posix(),
                          candidate_sha256=sha(dst), method="border_geometry.cutout with alternate painted core and original RGB restored",
                          radius_px=trial_radius, dimensions=list(Image.open(src).size),
                          rgb_changed_pixels=0, partial_alpha_edge_colored_pixels=edge_colored,
                          visible_pixels_outside_paper=0, geometry=geometry,
                          status="pending_visual_review")
            (QA / f"{aid}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(f"OK {aid} radius={trial_radius} edge_colored={edge_colored}", flush=True)
        except Exception as exc:
            print(f"REVIEW {aid}: {exc}", flush=True)


if __name__ == "__main__":
    main()
