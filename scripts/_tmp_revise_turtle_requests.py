import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batch = json.loads((ROOT / "state/twenty-pairs-20260924.json").read_text(encoding="utf-8"))
topic = next(item for item in batch["topics"] if item["slug"] == "little-turtle")
correction = (
    " Make this unmistakably a small freshwater turtle: a compact oval turtle head with a "
    "short blunt beak, eyes placed on the sides, a slender neck emerging from under a "
    "domed segmented shell, four separate short legs with small claws, and one visible "
    "short tail. Avoid a wide flat frog face, frog eye bumps, and frog-like forefeet."
)
for asset_id in topic["ids"]:
    if asset_id == "turtle-strawberry":
        continue
    path = ROOT / "state/requests" / f"{asset_id}.json"
    request = json.loads(path.read_text(encoding="utf-8"))
    needle = " Draw exactly one whole character with consistent anatomy and design across this topic:"
    assert needle in request["prompt"]
    request["prompt"] = request["prompt"].replace(needle, correction + needle)
    request["referenced_image_paths"] = [
        "references/Stickers/1_Animals/rabbit.png",
        "references/Stickers/1_Animals/cow.png",
    ]
    request["note"] = "Exact final prompt and original style refs; turtle anatomy clarification after first strawberry output looked frog-like."
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"revised_ids": [asset_id for asset_id in topic["ids"] if asset_id != "turtle-strawberry"]}))
