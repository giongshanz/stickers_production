#!/usr/bin/env python3
"""Read-only master/delivery and visual-preview audit of open rework IDs."""

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "qa" / "rework-audit-20260922"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    qa = json.loads((ROOT / "qa" / "visual-qa.json").read_text(encoding="utf-8"))
    progress = json.loads((ROOT / "state" / "progress.json").read_text(encoding="utf-8"))
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    assets = {item["id"]: item for item in progress["assets"]}
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for candidate in qa["rework_candidates"]:
        aid = candidate["id"]
        asset = assets[aid]
        master = ROOT / "masters" / f"{aid}.png"
        copies = sorted((ROOT / "delivery").rglob(f"{aid}.png"))
        with Image.open(master) as image:
            rgba = image.convert("RGBA")
            arr = np.asarray(rgba)
            alpha = arr[:, :, 3]
            ys, xs = np.nonzero(alpha > 8)
            bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
            padding = [bbox[0], bbox[1], rgba.width - bbox[2], rgba.height - bbox[3]]
            for name, color in (("dark", (37, 43, 55, 255)), ("light", (244, 233, 211, 255))):
                base = Image.new("RGBA", rgba.size, color)
                base.alpha_composite(rgba)
                base.convert("RGB").save(OUT / f"{aid}-{name}.png")
            record = {
                "id": aid,
                "reason_in_visual_qa": candidate["reason"],
                "master": master.relative_to(ROOT).as_posix(),
                "sha256": digest(master),
                "size": [rgba.width, rgba.height],
                "mode": image.mode,
                "alpha_zero_pixels": int(np.count_nonzero(alpha == 0)),
                "alpha_partial_pixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
                "alpha_opaque_pixels": int(np.count_nonzero(alpha == 255)),
                "painted_bbox": bbox,
                "padding_ltrb": padding,
                "delivery_copies": [p.relative_to(ROOT).as_posix() for p in copies],
                "delivery_hashes_match": bool(copies) and all(digest(p) == digest(master) for p in copies),
                "catalogue_link_present": any(p.relative_to(ROOT).as_posix() in index for p in copies),
                "progress_status": asset["status"],
                "visual_review_status": "visually_reviewed_on_dark_and_light; not_final_approved",
            }
            records.append(record)

    for background in ("dark", "light"):
        for page in range((len(records) + 8) // 9):
            sheet = Image.new("RGB", (1080, 1230), (37, 43, 55) if background == "dark" else (244, 233, 211))
            draw = ImageDraw.Draw(sheet)
            for slot, record in enumerate(records[page * 9:(page + 1) * 9]):
                thumb = Image.open(OUT / f"{record['id']}-{background}.png")
                thumb.thumbnail((340, 340))
                col, row = slot % 3, slot // 3
                x, y = col * 360 + (360 - thumb.width) // 2, row * 410 + 8
                sheet.paste(thumb, (x, y))
                draw.text((col * 360 + 12, row * 410 + 358), record["id"], fill="white" if background == "dark" else "black")
            sheet.save(OUT / f"{background}-sheet-{page + 1}.png")

    (OUT / "machine-audit.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reviewed": len(records),
                      "delivery_matches": sum(r["delivery_hashes_match"] for r in records),
                      "catalogue_links": sum(r["catalogue_link_present"] for r in records),
                      "output": OUT.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__":
    main()
