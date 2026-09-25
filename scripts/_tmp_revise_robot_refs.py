import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batch = json.loads((ROOT / "state/twenty-pairs-20260924.json").read_text(encoding="utf-8"))
topic = next(item for item in batch["topics"] if item["slug"] == "small-robot")
for asset_id in topic["ids"]:
    path = ROOT / "state/requests" / f"{asset_id}.json"
    request = json.loads(path.read_text(encoding="utf-8"))
    request["referenced_image_paths"] = [
        "references/Stickers/2. Home appliance/68-Home Appliance_2.png",
        "references/Stickers/8-Gardening/8-Gardening_1.png",
    ]
    request["note"] = "Exact final original references: warm painted cream appliance volume and muted teal watering-can finish. Avoid frog-shaped robot face."
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"revised_count": len(topic["ids"])}))
