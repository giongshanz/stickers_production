"""Trim stray white margin from a generated transparent sticker, alpha only."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from alpha_cleanup import connected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--margin", type=int, default=13)
    args = parser.parse_args()
    if args.destination.exists():
        raise SystemExit("Destination exists")
    rgba = np.asarray(Image.open(args.source).convert("RGBA")).copy()
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]
    chroma = rgb.max(axis=2).astype(np.int16) - rgb.min(axis=2).astype(np.int16)
    # The painted object is one connected region. Exclude pale cut paper and
    # detached flecks before measuring the margin around the actual artwork.
    colored = (alpha >= 128) & ((chroma >= 24) | (rgb.min(axis=2) < 165))
    joined = np.asarray(Image.fromarray(colored.astype("uint8") * 255).filter(ImageFilter.MaxFilter(5))) > 0
    ys, xs = np.nonzero(joined)
    if not len(xs):
        raise SystemExit("Cannot find painted foreground")
    nearest = np.argmin((xs - rgba.shape[1] / 2) ** 2 + (ys - rgba.shape[0] / 2) ** 2)
    core = connected(joined, [(int(xs[nearest]), int(ys[nearest]))])
    if core.sum() < 1000:
        raise SystemExit("Cannot find painted foreground")
    retained = np.asarray(Image.fromarray(core.astype("uint8") * 255).filter(ImageFilter.MaxFilter(2 * args.margin + 1))) > 0
    rgba[:, :, 3] = np.where(retained, alpha, 0)
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba).save(args.destination)
    check = np.asarray(Image.open(args.destination).convert("RGBA"))
    assert np.array_equal(check[:, :, :3], rgb)
    assert check.shape == rgba.shape


if __name__ == "__main__":
    main()
