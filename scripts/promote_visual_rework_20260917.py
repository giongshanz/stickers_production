#!/usr/bin/env python3
"""Select the reviewed September visual reworks and close stale alpha notes."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "revisions/rework-20260917"
ARCHIVE = BASE / "previous"
QA = ROOT / "qa/rework-20260917"
SELECTED = {
    "tailor-dress-form": "tailor-dress-form-v1.png",
    "terrarium-mister": "terrarium-mister-v1.png",
    "terrarium-moss": "terrarium-moss-v1.png",
    "snorkel-mask": "snorkel-mask-v1.png",
    "snorkel-tube": "snorkel-tube-v1.png",
    "dive-rashguard": "dive-rashguard-v1.png",
    "table-coral": "table-coral-v3.png",
    "coral-nursery-tree": "coral-nursery-tree-v1.png",
    "calligraphy-inkstone": "calligraphy-inkstone-v2.png",
    "bongos": "bongos-v1.png",
    "marching-trumpet": "marching-trumpet-v1.png",
    "dragonfly": "dragonfly-v1.png",
}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def main() -> None:
    progress = json.loads((ROOT / "state/progress.json").read_text(encoding="utf-8"))
    visual_path = ROOT / "qa/visual-qa.json"
    visual = json.loads(visual_path.read_text(encoding="utf-8"))
    reasons = {row["id"]: row["reason"] for row in visual["rework_candidates"]}
    if len(reasons) != 25 or len(SELECTED) != 12 or not set(SELECTED).issubset(reasons):
        raise ValueError("Unexpected visual QA candidate set")
    rows = {row["id"]: row for row in progress["assets"]}
    work = []
    for aid, filename in SELECTED.items():
        source = ROOT / f"masters/{aid}.png"
        candidate = BASE / filename
        if not candidate.is_file() or digest(source) != rows[aid]["sha256"]:
            raise ValueError(f"Candidate missing or source changed: {aid}")
        with Image.open(candidate) as im:
            if im.mode != "RGBA" or im.size != (rows[aid]["width"], rows[aid]["height"]):
                raise ValueError(f"Mode or dimensions changed: {aid}")
            alpha = np.asarray(im)[:, :, 3]
            if any(int(alpha[y, x]) for y, x in ((0, 0), (0, -1), (-1, 0), (-1, -1))):
                raise ValueError(f"Opaque corner: {aid}")
            yy, xx = np.where(alpha >= 128)
            if not len(xx) or min(xx.min(), im.width - 1 - xx.max(), yy.min(), im.height - 1 - yy.max()) < 25:
                raise ValueError(f"Insufficient clear padding: {aid}")
        deliveries = [ROOT / slot["file"] for slot in progress["topic_slots"] if slot["id"] == aid]
        if not deliveries or any(not path.is_file() or digest(path) != rows[aid]["sha256"] for path in deliveries):
            raise ValueError(f"Delivery mismatch: {aid}")
        archive = ARCHIVE / aid
        if archive.exists():
            raise ValueError(f"Archive already exists: {aid}")
        work.append((aid, source, candidate, deliveries, archive))
    print(f"PREFLIGHT {len(work)} masters and {sum(len(item[3]) for item in work)} delivery copies", flush=True)
    records = []
    for aid, source, candidate, deliveries, archive in work:
        old_hash = digest(source)
        new_hash = digest(candidate)
        old_master = archive / source.relative_to(ROOT)
        old_master.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(source, old_master)
        old_deliveries = []
        for path in deliveries:
            dest = archive / path.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(path, dest)
            old_deliveries.append(dest.relative_to(ROOT).as_posix())
        shutil.copy2(candidate, source)
        if digest(source) != new_hash or digest(old_master) != old_hash:
            raise ValueError(f"Promotion hash check failed: {aid}")
        record = {
            "id": aid,
            "selected_utc": datetime.now(timezone.utc).isoformat(),
            "reason": reasons[aid],
            "old_master": old_master.relative_to(ROOT).as_posix(),
            "old_sha256": old_hash,
            "old_deliveries": old_deliveries,
            "new_master": source.relative_to(ROOT).as_posix(),
            "new_sha256": new_hash,
            "selected_candidate": candidate.relative_to(ROOT).as_posix(),
            "review": "Subject, silhouette, padding and alpha visually reviewed on dark contact sheets; provisional art acceptance.",
        }
        write(QA / "selected" / f"{aid}.json", record)
        records.append(record)
        print(f"PROMOTED {aid}", flush=True)
    stale = sorted(set(reasons) - set(SELECTED))
    visual["rework_candidates"] = []
    visual["visual_rework_20260917_note"] = (
        "12 imagegen replacements selected and previous masters/delivery copies archived. "
        "13 prior alpha-only rework notes were visually rechecked on dark contact sheets "
        "after the earlier border-alpha cleanup and found resolved without another master edit. "
        "See qa/rework-20260917/selection-summary.json. Visual approval remains provisional."
    )
    write(visual_path, visual)
    write(QA / "selection-summary.json", {
        "selected_utc": datetime.now(timezone.utc).isoformat(),
        "replaced_count": len(records),
        "replaced_ids": list(SELECTED),
        "rechecked_existing_count": len(stale),
        "rechecked_existing_ids": stale,
        "review_contact_sheets": [
            "qa/rework-20260917/candidates-dark-1.png",
            "qa/rework-20260917/candidates-dark-2.png",
            "qa/rework-20260917/alpha-review-dark-1.png",
            "qa/rework-20260917/alpha-review-dark-2.png",
            "qa/rework-20260917/alpha-review-dark-3.png",
            "qa/rework-20260917/alpha-review-dark-4.png",
        ],
        "records": [f"qa/rework-20260917/selected/{aid}.json" for aid in SELECTED],
    })


if __name__ == "__main__":
    main()
