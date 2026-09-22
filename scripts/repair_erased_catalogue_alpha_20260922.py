"""Restore two over-trimmed sticker alpha channels from their saved originals.

Run without arguments to make light/dark before-and-after previews. After visual
review, run with --promote to archive and replace the selected PNGs. RGB pixels
and canvas dimensions must remain identical throughout.
"""

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "qa" / "catalogue-alpha-fix-20260922"
REV = ROOT / "revisions" / "catalogue-alpha-fix-20260922"
ITEMS = (
    (
        "access-hearing-aid",
        "revisions/generation-20260922-accessible-everyday/access-hearing-aid-v1.png",
        "delivery/stickers/accessible-everyday/access-hearing-aid.png",
        "2ced182d295a720a83f9189a2728103d91158aeb3fa34f493f282694570d4bca",
    ),
    (
        "railway-signal",
        "revisions/batch-20260918/railway-signal-v1.png",
        "delivery/stickers/railway-station/railway-signal.png",
        "c03a05cc5da282ad70522d07543c4f13b25c0edc6d216b475228224ab009b317",
    ),
)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def local(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Path escapes workspace: {relative}")
    return path


def inspect():
    records = []
    for aid, original_rel, delivery_rel, expected_old in ITEMS:
        master = local(f"masters/{aid}.png")
        original = local(original_rel)
        delivery = local(delivery_rel)
        if sha(master) != expected_old or sha(delivery) != expected_old:
            raise ValueError(f"Current files changed unexpectedly: {aid}")
        with Image.open(master) as image:
            before = image.convert("RGBA")
        with Image.open(original) as image:
            after = image.convert("RGBA")
        current = np.asarray(before)
        restored = np.asarray(after)
        if before.size != after.size or not np.array_equal(current[:, :, :3], restored[:, :, :3]):
            raise ValueError(f"RGB or dimensions differ: {aid}")
        if any(restored[y, x, 3] for x, y in ((0, 0), (after.width - 1, 0), (0, after.height - 1), (after.width - 1, after.height - 1))):
            raise ValueError(f"Original has nontransparent corner: {aid}")
        old_visible = int(np.count_nonzero(current[:, :, 3] >= 128))
        new_visible = int(np.count_nonzero(restored[:, :, 3] >= 128))
        if new_visible < old_visible * 3:
            raise ValueError(f"Original does not restore enough painted area: {aid}")
        records.append(dict(id=aid, master=master, original=original, delivery=delivery,
                            before=before, after=after, old_sha256=expected_old,
                            new_sha256=sha(original), size=list(after.size),
                            old_visible_pixels=old_visible, new_visible_pixels=new_visible))
    return records


def preview(records):
    OUT.mkdir(parents=True, exist_ok=True)
    for record in records:
        for background, color in (("light", (242, 233, 219, 255)), ("dark", (54, 59, 64, 255))):
            sheet = Image.new("RGB", (700, 390), color[:3])
            draw = ImageDraw.Draw(sheet)
            for index, label in enumerate(("before", "after")):
                image = record[label]
                composite = Image.new("RGBA", image.size, color)
                composite.alpha_composite(image)
                thumb = composite.convert("RGB")
                thumb.thumbnail((330, 330))
                sheet.paste(thumb, (index * 350 + (350 - thumb.width) // 2, 15))
                draw.text((index * 350 + 15, 355), label, fill="white" if background == "dark" else "black")
            sheet.save(OUT / f"{record['id']}-{background}.png")


def promote(records):
    previous = REV / "previous"
    targets = [p for r in records for p in (r["master"], r["delivery"])]
    archive_paths = [previous / p.relative_to(ROOT) for p in targets]
    if any(p.exists() for p in archive_paths) or (REV / "selection.json").exists():
        raise ValueError("Archive already exists; refusing to overwrite")
    for path, archive in zip(targets, archive_paths):
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, archive)
        if sha(archive) != sha(path):
            raise ValueError(f"Archive hash mismatch: {archive}")
    for record in records:
        for target in (record["master"], record["delivery"]):
            shutil.copy2(record["original"], target)
            if sha(target) != record["new_sha256"]:
                raise ValueError(f"Replacement hash mismatch: {target}")
    selection = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reason": "Catalogue thumbnails showed only thin white lines because alpha cleanup erased painted interiors; restore alpha from the saved original PNGs.",
        "method": "Selected saved original RGBA PNG bytes; verified RGB and canvas dimensions equal the old selected masters.",
        "items": [
            {key: value for key, value in r.items() if key in
             ("id", "old_sha256", "new_sha256", "size", "old_visible_pixels", "new_visible_pixels")}
            | {"original": r["original"].relative_to(ROOT).as_posix(),
               "master": r["master"].relative_to(ROOT).as_posix(),
               "delivery": r["delivery"].relative_to(ROOT).as_posix(),
               "archived_master": (previous / r["master"].relative_to(ROOT)).relative_to(ROOT).as_posix(),
               "archived_delivery": (previous / r["delivery"].relative_to(ROOT)).relative_to(ROOT).as_posix()}
            for r in records
        ],
    }
    REV.mkdir(parents=True, exist_ok=True)
    (REV / "selection.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args()
    records = inspect()
    preview(records)
    if args.promote:
        promote(records)
    print(json.dumps({"promoted": args.promote,
                      "preview_dir": OUT.relative_to(ROOT).as_posix(),
                      "items": [{key: r[key] for key in ("id", "old_sha256", "new_sha256", "old_visible_pixels", "new_visible_pixels")}
                                for r in records]}, indent=2))


if __name__ == "__main__":
    main()
