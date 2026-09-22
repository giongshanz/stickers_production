#!/usr/bin/env python3
"""Trial an alpha-only cleanup of one enclosed, near-white sticker opening.

The seed and tight box are chosen after visual inspection. The tool refuses a
component that reaches the box boundary, preserving nearby pale artwork.
It writes a candidate only; it never promotes a master or delivery copy.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from alpha_cleanup import connected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--seed", required=True, help="x,y within the opening")
    parser.add_argument("--box", required=True, help="x1,y1,x2,y2 around opening")
    parser.add_argument("--white-min", type=int, default=230)
    parser.add_argument("--chroma-max", type=int, default=22)
    parser.add_argument("--inset", type=int, default=2)
    args = parser.parse_args()

    x, y = (int(v) for v in args.seed.split(","))
    x1, y1, x2, y2 = (int(v) for v in args.box.split(","))
    src = np.asarray(Image.open(args.source).convert("RGBA")).copy()
    height, width = src.shape[:2]
    if not (0 <= x1 < x < x2 <= width and 0 <= y1 < y < y2 <= height):
        raise ValueError("Seed must be inside an in-canvas box")
    if not (0 <= args.inset <= 8):
        raise ValueError("Inset must be 0..8")

    rgb = src[y1:y2, x1:x2, :3]
    alpha = src[y1:y2, x1:x2, 3]
    low = rgb.min(axis=2)
    chroma = rgb.max(axis=2).astype(np.int16) - low.astype(np.int16)
    passable = ((low >= args.white_min) & (chroma <= args.chroma_max)) | (alpha < 64)
    if not passable[y - y1, x - x1]:
        raise ValueError("Seed is not near-white or transparent")
    hole = connected(passable, [(x - x1, y - y1)])
    if hole[0].any() or hole[-1].any() or hole[:, 0].any() or hole[:, -1].any():
        raise ValueError("Candidate reaches box boundary; narrow box or choose a different seed")
    if args.inset:
        for _ in range(args.inset):
            padded = np.pad(hole, 1, constant_values=False)
            hole = (padded[1:-1, 1:-1] & padded[:-2, 1:-1] &
                    padded[2:, 1:-1] & padded[1:-1, :-2] & padded[1:-1, 2:])
    cleared = int(np.count_nonzero(alpha[hole]))
    if cleared < 20:
        raise ValueError(f"Too few opaque pixels to clear: {cleared}")
    alpha[hole] = 0
    dest = Path(args.destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(src, "RGBA").save(dest)
    check = np.asarray(Image.open(dest).convert("RGBA"))
    original = np.asarray(Image.open(args.source).convert("RGBA"))
    assert check.shape == original.shape
    assert np.array_equal(check[:, :, :3], original[:, :, :3])
    assert np.all(check[:, :, 3] <= original[:, :, 3])
    print(json.dumps({"source": args.source, "destination": args.destination,
                      "seed": [x, y], "box": [x1, y1, x2, y2],
                      "inset": args.inset, "cleared_pixels": cleared,
                      "rgb_unchanged": True, "dimensions": [width, height]}, indent=2))


if __name__ == "__main__":
    main()
