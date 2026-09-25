import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batch = json.loads((ROOT / "state/twenty-pairs-20260924.json").read_text(encoding="utf-8"))
topic = next(item for item in batch["topics"] if item["slug"] == "fox-explorer")
needle = " Draw exactly one whole character with consistent anatomy and design across this topic:"
correction = (
    " Keep fox anatomy unmistakable: a narrow pointed muzzle, two tall triangular ears, "
    "a long rust-red bushy tail with only a cream tip, and four complete paws. No "
    "raccoon eye mask, ringed tail, rabbit ears or frog face."
)
for asset_id in topic["ids"]:
    path = ROOT / "state/requests" / f"{asset_id}.json"
    request = json.loads(path.read_text(encoding="utf-8"))
    assert needle in request["prompt"]
    request["prompt"] = request["prompt"].replace(needle, correction + needle)
    request["referenced_image_paths"] = [
        "references/Stickers/3. Racoon/187-Racoon_1.png",
        "references/Stickers/1_Animals/rabbit.png",
    ]
    request["note"] = "Exact final original style refs and explicit fox anatomy; do not copy raccoon mask or rabbit ears."
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"revised_count": len(topic["ids"])}))
