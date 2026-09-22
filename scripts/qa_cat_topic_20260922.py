"""Inspect the eight selected cat PNGs on light/dark catalogue-like backgrounds."""

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "qa" / "cat-collection-20260922"
IDS = (
    "cat-gray-tabby", "cat-black", "cat-tuxedo", "cat-calico",
    "cat-siamese", "cat-white-longhair", "cat-orange-kitten", "cat-blue-shorthair",
)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    report = []
    sheets = {name: Image.new("RGB", (1280, 800), color[:3]) for name, color in
              (("light", (234, 224, 210, 255)), ("dark", (54, 59, 64, 255)))}
    for slot, aid in enumerate(IDS):
        master = ROOT / "masters" / f"{aid}.png"
        delivery = ROOT / "delivery" / "stickers" / "cat-collection" / f"{aid}.png"
        with Image.open(master) as image:
            rgba = image.convert("RGBA")
        alpha = np.asarray(rgba)[:, :, 3]
        ys, xs = np.nonzero(alpha > 8)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        report.append({
            "id": aid,
            "master": master.relative_to(ROOT).as_posix(),
            "delivery": delivery.relative_to(ROOT).as_posix(),
            "sha256": digest(master),
            "delivery_matches": delivery.is_file() and digest(delivery) == digest(master),
            "catalogue_link_present": delivery.relative_to(ROOT).as_posix() in index,
            "actual_size": list(rgba.size),
            "corner_alpha": [int(alpha[y, x]) for y, x in
                             ((0, 0), (0, rgba.width - 1), (rgba.height - 1, 0),
                              (rgba.height - 1, rgba.width - 1))],
            "visible_bbox_alpha_gt_8": bbox,
            "padding_ltrb": [bbox[0], bbox[1], rgba.width - bbox[2], rgba.height - bbox[3]],
            "visible_pixels_alpha_ge_128": int(np.count_nonzero(alpha >= 128)),
        })
        col, row = slot % 4, slot // 4
        for name, color in (("light", (234, 224, 210, 255)), ("dark", (54, 59, 64, 255))):
            composite = Image.new("RGBA", rgba.size, color)
            composite.alpha_composite(rgba)
            composite.convert("RGB").save(OUT / f"{aid}-{name}.png")
            thumb = composite.convert("RGB")
            thumb.thumbnail((300, 320), Image.Resampling.LANCZOS)
            x = col * 320 + (320 - thumb.width) // 2
            y = row * 400 + (340 - thumb.height) // 2
            sheets[name].paste(thumb, (x, y))
            draw = ImageDraw.Draw(sheets[name])
            draw.text((col * 320 + 12, row * 400 + 355), aid,
                      fill="white" if name == "dark" else "black")
    for name, sheet in sheets.items():
        sheet.save(OUT / f"{name}-sheet.png")
    (OUT / "machine-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reviewed": len(report),
                      "delivery_matches": sum(x["delivery_matches"] for x in report),
                      "catalogue_links": sum(x["catalogue_link_present"] for x in report),
                      "min_padding": min(min(x["padding_ltrb"]) for x in report)}, indent=2))


if __name__ == "__main__":
    main()
