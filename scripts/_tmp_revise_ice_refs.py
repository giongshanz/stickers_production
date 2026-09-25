import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batch = json.loads((ROOT / "state/twenty-pairs-20260924.json").read_text(encoding="utf-8"))
topic = next(item for item in batch["topics"] if item["slug"] == "ice-day")
for asset_id in topic["ids"]:
    if asset_id == "seal-ice-skates":
        continue
    path = ROOT / "state/requests" / f"{asset_id}.json"
    request = json.loads(path.read_text(encoding="utf-8"))
    request["referenced_image_paths"] = [
        "references/Stickers/33_Winter/33- winter_5.png" if asset_id == "ice-sled" else "references/Stickers/33_Winter/33- winter_1.png",
        "references/Stickers/33_Winter/33- winter_2.png",
    ]
    request["note"] = "Exact final original winter style references; the prior pair pointed to duplicate copies of the same boots image."
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"revised_count": 7}))
