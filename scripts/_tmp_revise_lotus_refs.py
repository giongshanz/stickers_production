import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batch = json.loads((ROOT / "state/twenty-pairs-20260924.json").read_text(encoding="utf-8"))
topic = next(item for item in batch["topics"] if item["slug"] == "lotus-pond")
for asset_id in topic["ids"]:
    if asset_id in {"turtle-lotus-leaf", "lotus-frog"}:
        continue
    path = ROOT / "state/requests" / f"{asset_id}.json"
    request = json.loads(path.read_text(encoding="utf-8"))
    request["referenced_image_paths"] = [
        "references/Stickers/3_Flowers/Flower_3.png",
        "references/Stickers/Fish/46-fish_1.png" if asset_id == "lotus-pond-fish" else "references/Stickers/8-Gardening/8-Gardening_1.png",
    ]
    request["note"] = "Exact final original style references selected for this subject; no frog reference for non-frog lotus objects."
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"revised_count": 6}))
