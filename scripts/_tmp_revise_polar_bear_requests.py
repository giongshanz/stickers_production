import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batch = json.loads((ROOT / "state/twenty-pairs-20260924.json").read_text(encoding="utf-8"))
topic = next(item for item in batch["topics"] if item["slug"] == "polar-bear-activities")
needle = " Draw exactly one whole character with consistent anatomy and design across this topic:"
correction = (
    " This must read as one ivory-white polar bear cub: small round bear ears, a "
    "protruding cream bear muzzle, a charcoal nose and four short bear paws. No black "
    "panda eye patches or limbs, no rabbit ears and no frog face."
)
for asset_id in topic["ids"]:
    path = ROOT / "state/requests" / f"{asset_id}.json"
    request = json.loads(path.read_text(encoding="utf-8"))
    assert needle in request["prompt"]
    request["prompt"] = request["prompt"].replace(needle, correction + needle)
    request["referenced_image_paths"] = [
        "references/Stickers/1_Animals/panda.png",
        "references/Stickers/1_Animals/rabbit.png",
    ]
    request["note"] = "Exact final original style references and polar bear anatomy; avoid copying panda markings or rabbit ears."
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"revised_count": len(topic["ids"])}))
