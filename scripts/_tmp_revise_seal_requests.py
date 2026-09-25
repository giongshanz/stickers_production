import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batch = json.loads((ROOT / "state/twenty-pairs-20260924.json").read_text(encoding="utf-8"))
topic = next(item for item in batch["topics"] if item["slug"] == "seal-activities")
needle = " Draw exactly one whole character with consistent anatomy and design across this topic:"
correction = (
    " Make the anatomy unmistakably that of a harbor seal: a smooth tapered body, short "
    "whiskered muzzle, no external ear flaps, no paws or legs, two distinct short front "
    "flippers and two tapered rear flippers. Avoid frog-like or rabbit-like anatomy."
)
for asset_id in topic["ids"]:
    path = ROOT / "state/requests" / f"{asset_id}.json"
    request = json.loads(path.read_text(encoding="utf-8"))
    assert needle in request["prompt"]
    request["prompt"] = request["prompt"].replace(needle, correction + needle)
    request["referenced_image_paths"] = [
        "references/Stickers/19_MarineLife/marine_life_1.png",
        "references/Stickers/1_Animals/rabbit.png",
    ]
    request["note"] = "Exact final original style references and explicit seal anatomy; references are not subjects."
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"revised_count": len(topic["ids"])}))
