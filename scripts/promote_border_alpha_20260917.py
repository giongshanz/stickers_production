#!/usr/bin/env python3
"""Promote visually reviewed alpha-only candidates, preserving every old copy."""
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
QA = ROOT / "qa/border-alpha-20260917"
ARCHIVE = ROOT / "revisions/border-alpha-20260917/previous"
EXCEPTIONS = ("stage-spotlight", "foraging-knife", "panda-plant-pot", "wild-garlic-bundle")


def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def main():
    progress = read(ROOT / "state/progress.json")
    rows = [r for r in progress["assets"] if r["status"] == "needs_alpha"]
    if len(rows) != 77:
        raise ValueError(f"Expected 77 pending old images, got {len(rows)}")
    selected = []
    for row in rows:
        aid = row["id"]
        report = read(QA / ("exceptions" if aid in EXCEPTIONS else "") / f"{aid}.json")
        candidate = (ROOT / report["candidate"]).resolve()
        if aid == "stage-spotlight":
            candidate = ROOT / "revisions/border-alpha-20260917-exceptions/stage-spotlight-hole-v2.png"
        source = ROOT / f"masters/{aid}.png"
        if digest(source) != row["sha256"] or digest(source) != report["source_sha256"]:
            raise ValueError(f"Source changed: {aid}")
        if not candidate.is_file() or not candidate.resolve().is_relative_to(ROOT):
            raise ValueError(f"Candidate missing/outside workspace: {aid}")
        if aid != "stage-spotlight" and digest(candidate) != report["candidate_sha256"]:
            raise ValueError(f"Candidate changed: {aid}")
        src = np.asarray(Image.open(source).convert("RGB"))
        dst = np.asarray(Image.open(candidate).convert("RGBA"))
        if dst.shape != (src.shape[0], src.shape[1], 4) or not np.array_equal(dst[:, :, :3], src):
            raise ValueError(f"RGB or dimensions changed: {aid}")
        if [int(dst[0, 0, 3]), int(dst[0, -1, 3]), int(dst[-1, 0, 3]), int(dst[-1, -1, 3])] != [0] * 4:
            raise ValueError(f"Nontransparent corners: {aid}")
        deliveries = [ROOT / s["file"] for s in progress["topic_slots"] if s["id"] == aid]
        if not deliveries or any(not p.is_file() or digest(p) != row["sha256"] for p in deliveries):
            raise ValueError(f"Delivery does not match source: {aid}")
        archive_dir = ARCHIVE / aid
        if archive_dir.exists():
            raise ValueError(f"Archive already exists: {aid}")
        selected.append((aid, source, candidate, deliveries, archive_dir))
    print(f"PREFLIGHT {len(selected)} images and {sum(len(x[3]) for x in selected)} delivery copies", flush=True)
    for aid, source, candidate, deliveries, archive_dir in selected:
        old_hash = digest(source)
        new_hash = digest(candidate)
        backup_master = archive_dir / f"masters/{aid}.png"
        backup_master.parent.mkdir(parents=True, exist_ok=True)
        # Old master and each old delivery copy are moved into their own
        # revision paths, so refresh cannot mistake them for current exports.
        shutil.move(source, backup_master)
        for path in deliveries:
            backup = archive_dir / path.relative_to(ROOT)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(path, backup)
        shutil.copy2(candidate, source)
        if digest(source) != new_hash or digest(backup_master) != old_hash:
            raise ValueError(f"Promotion hash mismatch: {aid}")
        record = dict(id=aid, selected_utc=datetime.now(timezone.utc).isoformat(),
                      reason="User-approved 2026-09-17 alpha-only geometric background removal; visually reviewed on dark contact sheets.",
                      old_master=backup_master.relative_to(ROOT).as_posix(), old_sha256=old_hash,
                      old_deliveries=[(archive_dir / p.relative_to(ROOT)).relative_to(ROOT).as_posix() for p in deliveries],
                      new_master=source.relative_to(ROOT).as_posix(), new_sha256=new_hash,
                      selected_candidate=candidate.relative_to(ROOT).as_posix(),
                      rgb_unchanged=True, dimensions_unchanged=True,
                      alpha_review="provisional; other visual-rework notes in qa/visual-qa.json remain open")
        write(QA / "selected" / f"{aid}.json", record)
        print(f"PROMOTED {aid}", flush=True)
    write(QA / "selection-summary.json", dict(selected_utc=datetime.now(timezone.utc).isoformat(),
          selected_count=len(selected), ids=[x[0] for x in selected],
          note="Source RGB and canvas dimensions verified identical; original masters and all previous delivery copies preserved under revisions."))


if __name__ == "__main__":
    main()
