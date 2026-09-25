#!/usr/bin/env python3
"""Record a reviewed production checkpoint for the 20-topic batch."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "state" / "twenty-pairs-20260924.json"
WORK = ROOT / "state" / "work-order.json"
QA = ROOT / "qa" / "visual-qa.json"
REPORT = ROOT / "qa" / "twenty-pairs-20260924" / "CHECKPOINT.vi.md"

parser = argparse.ArgumentParser()
parser.add_argument("--reviewed-slugs", nargs="*", default=[])
parser.add_argument("--quota-reached", action="store_true")
parser.add_argument("--quota-reset-unix", type=int)
args = parser.parse_args()
today = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
reset_utc = (
    datetime.fromtimestamp(args.quota_reset_unix, timezone.utc)
    if args.quota_reset_unix else None
)
reset_local = reset_utc.astimezone(ZoneInfo("Asia/Ho_Chi_Minh")) if reset_utc else None

batch = json.loads(BATCH.read_text(encoding="utf-8"))
topics = batch["topics"]
valid_slugs = {topic["slug"] for topic in topics}
assert set(args.reviewed_slugs) <= valid_slugs
qa = json.loads(QA.read_text(encoding="utf-8"))
reviewed = set(qa["reviewed_ids"])
for slug in args.reviewed_slugs:
    topic = next(topic for topic in topics if topic["slug"] == slug)
    assert all((ROOT / "masters" / f"{asset_id}.png").is_file() for asset_id in topic["ids"])
    for mode in ("light", "dark"):
        assert (ROOT / "qa" / "twenty-pairs-20260924" / f"{slug}-{mode}.png").is_file()
    for asset_id in topic["ids"]:
        if asset_id not in reviewed:
            qa["reviewed_ids"].append(asset_id)
            reviewed.add(asset_id)
qa["twenty_pairs_20260924_note"] = (
    "Production underway for 20 user-approved topics in ten one-sticker-sharing pairs. "
    "Completed topics are provisionally reviewed on light and dark contact sheets as listed in "
    "qa/twenty-pairs-20260924/CHECKPOINT.vi.md. Chestnut-leaf-cluster was replaced because the "
    "original looked like oak leaves and acorns; see revisions/twenty-pairs-20260924/chestnut-leaf-cluster-before. "
    "All newly selected alpha cleanup preserves RGB and canvas dimensions. In-game-scale QA and the "
    "25 earlier visual rework candidates remain open."
)
QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ids = list(dict.fromkeys(asset_id for topic in topics for asset_id in topic["ids"]))
generated = [asset_id for asset_id in ids if (ROOT / "masters" / f"{asset_id}.png").is_file()]
missing = [asset_id for asset_id in ids if asset_id not in generated]
complete_topics = [topic for topic in topics if all(asset_id in generated for asset_id in topic["ids"])]
work = json.loads(WORK.read_text(encoding="utf-8"))
work["active_batch_ids"] = ids
work["next_action"] = (
    f"Resume twenty-pair batch from {missing[0]} after imagegen quota resets; {len(missing)} unique masters remain."
    if args.quota_reached else
    (f"Continue twenty-pair batch from {missing[0]}; {len(missing)} unique masters remain."
     if missing else "All new masters present; complete visual QA and verify.")
)
work["quota_status"] = (
    {
        "state": "usage_limit_reached",
        "failed_id": missing[0],
        "resets_at_unix": args.quota_reset_unix,
        "resets_at_utc": reset_utc.isoformat().replace("+00:00", "Z") if reset_utc else None,
        "last_success_date": today,
        "note": "Built-in imagegen returned HTTP 429; stop generation until quota is available. No alternate account or tool.",
    }
    if args.quota_reached else
    {
        "state": "available_at_last_request",
        "last_success_date": today,
        "note": f"{len(generated)} of 150 new masters generated so far; availability must be checked from next tool response.",
    }
)
WORK.write_text(json.dumps(work, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if args.quota_reached:
    error_log = ROOT / "state" / "imagegen-errors.jsonl"
    with error_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "time_utc": datetime.now(timezone.utc).isoformat(),
            "id": missing[0],
            "error_type": "usage_limit_reached",
            "http_status": 429,
            "resets_at_unix": args.quota_reset_unix,
            "note": "Built-in imagegen returned a usage limit response; no image was saved for this ID.",
        }, ensure_ascii=False) + "\n")

completed_names = ", ".join(topic["name_vi"] for topic in complete_topics)
reviewed_names = ", ".join(next(t["name_vi"] for t in topics if t["slug"] == slug) for slug in args.reviewed_slugs)
report = f"""# Checkpoint 20 topic — {today}

- Mục tiêu: 20 topic, 160 slot, 150 master mới, 10 sticker dùng chung.
- Đã có: {len(generated)}/150 master mới; còn {len(missing)}. Topic đủ ảnh: {len(complete_topics)}/20.
- Các topic đủ ảnh: {completed_names or 'chưa có'}.
- Topic đã xem sheet sáng/tối trong lượt checkpoint này: {reviewed_names or 'chưa có'}.
- ID tiếp theo: `{missing[0] if missing else 'không còn'}`.
- `chestnut-leaf-cluster` đã thay bản vì bản đầu có lá và quả giống sồi; bản cũ, delivery cũ và hash được lưu trong `revisions/twenty-pairs-20260924/chestnut-leaf-cluster-before/`.
- Alpha-only cleanup chỉ đặt alpha 1..15 về 0, giữ nguyên RGB và kích thước. Xem `qa/twenty-pairs-20260924/alpha-cleanup.json`.
- 25 rework cũ và QA ở kích thước game vẫn đang mở.
{('- Imagegen báo HTTP 429 `usage_limit_reached` ở `' + missing[0] + '`. Dự kiến reset ' + reset_local.strftime('%H:%M:%S %d/%m/%Y') + ' giờ Việt Nam; dừng tạo ảnh cho tới khi quota khả dụng.' if args.quota_reached and reset_local else ('- Imagegen báo HTTP 429 `usage_limit_reached`; dừng tạo ảnh cho tới khi quota khả dụng.' if args.quota_reached else ''))}
"""
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(report, encoding="utf-8")

start = ROOT / "START_HERE.vi.md"
body = start.read_text(encoding="utf-8")
marker = "## Đang triển khai 20 topic theo 10 cặp — 24/09/2026"
if marker not in body:
    body += f"\n\n{marker}\n\n- Mục tiêu mới: 102 topic, 816 slot, 796 master duy nhất; 20 ID dùng chung.\n- Xem checkpoint mới nhất tại `qa/twenty-pairs-20260924/CHECKPOINT.vi.md` và trạng thái trong `state/resume.json`.\n"
    start.write_text(body, encoding="utf-8")
print(json.dumps({"generated": len(generated), "missing": len(missing), "complete_topics": len(complete_topics), "next_id": missing[0] if missing else None}, ensure_ascii=False))
