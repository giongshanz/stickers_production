import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "plan" / "sticker-plan.json"
WORK = ROOT / "state" / "work-order.json"
REQUESTS = ROOT / "state" / "requests"
SLUGS = {
    "squirrel-forest", "chestnut-season", "happy-hedgehog", "pumpkin-season",
    "raccoon-activities", "lakeside-camping", "school-mouse", "art-corner",
    "winter-lamb", "knitwear", "little-turtle", "lotus-pond", "small-robot",
    "bicycles", "seal-activities", "ice-day", "polar-bear-activities",
    "fruit-ice-cream", "fox-explorer", "hot-air-balloons",
}

plan = json.loads(PLAN.read_text(encoding="utf-8"))
new_topics = [topic for topic in plan["topics"] if topic["slug"] in SLUGS]
assert len(new_topics) == 20
ids = list(dict.fromkeys(asset_id for topic in new_topics for asset_id in topic["asset_ids"]))
assert len(ids) == 150
idset = set(ids)
for asset in plan["assets"]:
    if asset["id"] in idset and asset["subject"].startswith("Exactly one whole the same "):
        asset["subject"] = "Draw the same " + asset["subject"][len("Exactly one whole the same "):]
PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

spec = importlib.util.spec_from_file_location("workspace_tool", ROOT / "scripts" / "workspace.py")
workspace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workspace)
REQUESTS.mkdir(parents=True, exist_ok=True)
for asset_id in ids:
    req = workspace.request_for(asset_id)
    (REQUESTS / f"{asset_id}.json").write_text(json.dumps(req, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

work = json.loads(WORK.read_text(encoding="utf-8"))
work["latest_user_instruction"] = (
    "2026-09-24: User approved twenty topics in ten pairs, eight sticker slots per topic and "
    "one shared master per pair. Produce all 150 new unique masters in plan order."
)
work["active_batch_ids"] = ids
work["next_action"] = f"Generate {ids[0]} next, then continue all 150 requested unique IDs in order."
WORK.write_text(json.dumps(work, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

summary = {
    "topics": [{"slug": t["slug"], "name_vi": t["name_vi"], "ids": t["asset_ids"]} for t in new_topics],
    "shared": [entry for entry in plan["shared_assets"] if entry["id"] in idset],
    "target_new_unique": len(ids),
    "target_new_slots": sum(len(t["asset_ids"]) for t in new_topics),
    "next_id": ids[0],
}
out = ROOT / "state" / "twenty-pairs-20260924.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"topic_count": len(new_topics), "new_slots": summary["target_new_slots"], "new_unique": len(ids), "shared": len(summary["shared"]), "next_id": ids[0]}, ensure_ascii=False))
