import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ID = "chestnut-leaf-cluster"
master = ROOT / "masters" / f"{ID}.png"
candidate = ROOT / "revisions" / "twenty-pairs-20260924" / f"{ID}-v2.png"
revision = ROOT / "revisions" / "twenty-pairs-20260924" / "chestnut-leaf-cluster-before"
revision.mkdir(parents=True, exist_ok=True)
old_master = revision / "master.png"
assert master.is_file() and candidate.is_file() and not old_master.exists()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

with Image.open(candidate) as image:
    assert image.mode == "RGBA" and image.width > 0 and image.height > 0

old_hash = sha(master)
new_hash = sha(candidate)
shutil.copy2(master, old_master)
delivery_archives = []
for path in (ROOT / "delivery").rglob(f"{ID}.png"):
    relative = path.relative_to(ROOT)
    archive = revision / relative
    archive.parent.mkdir(parents=True, exist_ok=True)
    assert not archive.exists()
    shutil.copy2(path, archive)
    delivery_archives.append(archive.relative_to(ROOT).as_posix())
    path.unlink()
shutil.copy2(candidate, master)
assert sha(master) == new_hash
report = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "id": ID,
    "reason": "First image resembled oak leaves and acorns; replacement has serrated chestnut leaves, spiky burr and smooth chestnuts.",
    "old_master": old_master.relative_to(ROOT).as_posix(),
    "old_sha256": old_hash,
    "archived_deliveries": delivery_archives,
    "candidate": candidate.relative_to(ROOT).as_posix(),
    "new_master": master.relative_to(ROOT).as_posix(),
    "new_sha256": new_hash,
    "request": f"state/requests/{ID}-v2.json",
}
(revision / "promotion.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
