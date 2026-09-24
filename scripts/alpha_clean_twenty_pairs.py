#!/usr/bin/env python3
"""Archive and clean only faint alpha (1..15) for the current 20-topic batch."""

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "state" / "twenty-pairs-20260924.json"
REPORT = ROOT / "qa" / "twenty-pairs-20260924" / "alpha-cleanup.json"
REVISION = ROOT / "revisions" / "twenty-pairs-20260924" / "alpha-before"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


batch = json.loads(BATCH.read_text(encoding="utf-8"))
ids = list(dict.fromkeys(asset_id for topic in batch["topics"] for asset_id in topic["ids"]))
assert len(ids) == 150
report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {"rows": []}
done = {row["id"] for row in report["rows"]}
processed = 0
for asset_id in ids:
    master = ROOT / "masters" / f"{asset_id}.png"
    if not master.is_file() or asset_id in done:
        continue
    archive = REVISION / "masters" / master.name
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        raise RuntimeError(f"Unlogged existing archive for {asset_id}")
    shutil.copy2(master, archive)
    delivery_archives = []
    deliveries = list((ROOT / "delivery").rglob(f"{asset_id}.png"))
    for delivery in deliveries:
        previous = REVISION / delivery.relative_to(ROOT)
        previous.parent.mkdir(parents=True, exist_ok=True)
        if previous.exists():
            raise RuntimeError(f"Unlogged existing delivery archive for {asset_id}")
        shutil.copy2(delivery, previous)
        delivery_archives.append(previous.relative_to(ROOT).as_posix())
    before_sha = sha(master)
    with Image.open(master) as image:
        original_size = image.size
        original_rgb = np.asarray(image.convert("RGB")).copy()
        rgba = np.asarray(image.convert("RGBA")).copy()
    alpha = rgba[:, :, 3]
    faint = (alpha >= 1) & (alpha <= 15)
    pixels_changed = int(faint.sum())
    alpha[faint] = 0
    Image.fromarray(rgba, mode="RGBA").save(master)
    with Image.open(master) as check:
        out = np.asarray(check.convert("RGBA"))
        assert check.size == original_size
        assert np.array_equal(out[:, :, :3], original_rgb)
    for delivery in deliveries:
        delivery.unlink()
    report["rows"].append({
        "id": asset_id,
        "master_before": archive.relative_to(ROOT).as_posix(),
        "delivery_before": delivery_archives,
        "before_sha256": before_sha,
        "after_sha256": sha(master),
        "dimensions": list(original_size),
        "rgb_unchanged": True,
        "dimensions_unchanged": True,
        "alpha_1_to_15_cleared": pixels_changed,
    })
    report["updated_utc"] = datetime.now(timezone.utc).isoformat()
    report["operation"] = "Set alpha 1..15 to zero only, preserving RGB and dimensions."
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    done.add(asset_id)
    processed += 1
print(json.dumps({"processed_now": processed, "total_processed": len(report["rows"]), "target": len(ids)}, ensure_ascii=False))
