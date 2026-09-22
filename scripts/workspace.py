#!/usr/bin/env python3
"""Portable sticker inventory. Reads PNG pixels; never edits or resizes images."""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import html
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
from datetime import datetime, timezone
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SAFE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def now():
    return datetime.now(timezone.utc).isoformat()

def local(name):
    p = Path(name)
    if p.is_absolute() or re.match(r"^[A-Za-z]:", str(name)):
        raise ValueError(f"Expected workspace-relative path: {name}")
    p = (ROOT / p).resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError(f"Path escapes workspace: {name}")
    return p

def read(name):
    return json.loads(local(name).read_text(encoding="utf-8-sig"))

def write(name, value):
    p = local(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_name(p.name + ".tmp")
    temp.write_text(value, encoding="utf-8", newline="\n")
    os.replace(temp, p)

def write_json(name, value):
    write(name, json.dumps(value, ensure_ascii=False, indent=2) + "\n")

def digest(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def copy_exact(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected = digest(source)
    if destination.exists():
        if digest(destination) != expected:
            raise ValueError(f"Existing file differs; preserve/review revision first: {destination}")
    else:
        with source.open("rb") as src, destination.open("xb") as dst:
            shutil.copyfileobj(src, dst)
    if digest(destination) != expected:
        raise ValueError(f"Copy hash mismatch: {destination}")

def plan():
    p = read("plan/sticker-plan.json")
    assets = {a["id"]: a for a in p["assets"]}
    target = p["target"]
    assert len(assets) == len(p["assets"]) == target["unique_assets"], "Distinct asset count differs from plan"
    assert len(p["topics"]) == target["topics"]
    assert len({t["slug"] for t in p["topics"]}) == target["topics"]
    assert target["total_topic_slots"] == target["topics"] * target["slots_per_topic"]
    uses = collections.defaultdict(list)
    for a in assets:
        assert SAFE_ID.fullmatch(a), f"Unsafe asset ID: {a}"
    for t in p["topics"]:
        assert SAFE_ID.fullmatch(t["slug"])
        assert len(t["asset_ids"]) == len(set(t["asset_ids"])) == target["slots_per_topic"]
        for a in t["asset_ids"]:
            assert a in assets
            uses[a].append(t["slug"])
    assert set(uses) == set(assets)
    assert all(len(u) in (1, 2) for u in uses.values())
    actual = {a: sorted(u) for a, u in uses.items() if len(u) == 2}
    declared = {a["id"]: sorted(a["topic_slugs"]) for a in p["shared_assets"]}
    assert len(actual) == len(p["shared_assets"]) == target["shared_assets"] and actual == declared
    spec = p["output_spec"]
    assert spec["target_width"] == spec["target_height"] == 512
    assert spec["prompt_target_only"] and not spec["scripted_resizing"]
    assert p["style_reference"] == "references/Stickers"
    return p, assets, uses

def png_info(path):
    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError("Install the read-only PNG dependency: python -m pip install -r requirements.txt")
    with Image.open(path) as im:
        assert im.format == "PNG", f"Not PNG: {path}"
        im.load()
        w, h = im.size
        alpha = im.getchannel("A") if "A" in im.getbands() else None
        if alpha is None and "transparency" in im.info:
            alpha = im.convert("RGBA").getchannel("A")
        corners = [alpha.getpixel(xy) for xy in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))] if alpha else [255]*4
        box = alpha.getbbox() if alpha else (0,0,w,h)
        hist = alpha.histogram() if alpha else [0]*255 + [w*h]
        padding = [box[0], box[1], w-box[2], h-box[3]] if box else [w,h,w,h]
        return dict(width=w, height=h, mode=im.mode, corner_alpha=corners,
                    transparent_pixels=hist[0], partial_alpha_pixels=sum(hist[1:255]),
                    opaque_pixels=hist[255], padding_nonzero_alpha=padding,
                    review_edge=min(padding) < .02 * min(w,h),
                    status="alpha_corners_clear" if corners == [0]*4 else "needs_alpha")

def inventory():
    p, assets, uses = plan()
    qa = read("qa/visual-qa.json")
    rework = {r["id"]: r["reason"] for r in qa["rework_candidates"]}
    rows = []
    for a in p["assets"]:
        rel = "masters/" + a["id"] + ".png"
        row = dict(id=a["id"], subject=a["subject"], topic_slugs=uses[a["id"]],
                   source=rel, status="missing", review_note=rework.get(a["id"], ""))
        if local(rel).exists():
            row.update(png_info(local(rel)))
            row.update(sha256=digest(local(rel)), bytes=local(rel).stat().st_size)
        rows.append(row)
    extra = set(f.stem for f in local("masters").glob("*.png")) - set(assets)
    assert not extra, f"Unplanned masters: {sorted(extra)}"
    by_id = {r["id"]: r for r in rows}
    topic_rows = []
    for t in p["topics"]:
        present = sum(by_id[a]["status"] != "missing" for a in t["asset_ids"])
        topic_rows.append(dict(slug=t["slug"], name_vi=t["name_vi"], generated=present,
                               target=p["target"]["slots_per_topic"]))
    counts = collections.Counter(r["status"] for r in rows)
    target = p["target"]
    summary = dict(target_topics=target["topics"], target_slots=target["total_topic_slots"],
                   target_unique=target["unique_assets"],
                   generated_unique=target["unique_assets"]-counts["missing"], missing_unique=counts["missing"],
                   alpha_corners_clear_unique=counts["alpha_corners_clear"],
                   needs_alpha_unique=counts["needs_alpha"],
                   topics_with_all_images=sum(t["generated"] == t["target"] for t in topic_rows),
                   generated_topic_slots=sum(t["generated"] for t in topic_rows),
                   visual_rework_unique=len(rework), complete=False)
    return p, rows, topic_rows, summary

def request_for(asset_id):
    p, assets, uses = plan()
    a = assets[asset_id]
    profiles = read("prompts/reference-profiles.json")
    topic = uses[asset_id][0]
    profile = profiles["topic_profiles"].get(topic, "objects")
    profile = profiles["asset_profiles"].get(asset_id, profile)
    spec = profiles["profiles"][profile]
    for r in spec["references"]:
        assert local(r).is_file(), f"Missing style reference: {r}"
    base = local("prompts/style-prompt-compact.txt").read_text(encoding="utf-8-sig").strip()
    prompt = base + "\nSUBJECT: " + a["subject"].rstrip(". ") + ". " + spec["suffix"]
    return dict(id=asset_id, subject=a["subject"], topic_slugs=uses[asset_id],
                profile=profile, prompt=prompt, referenced_image_paths=spec["references"],
                paths_relative_to="workspace root", target_dimensions=[512,512],
                target_only=True, scripted_resizing=False, tool="built-in imagegen",
                note="View the referenced images, then resolve their paths against the current workspace root when calling the image tool.")

def ordered_missing(p, rows):
    missing = {r["id"] for r in rows if r["status"] == "missing"}
    topics = p["topics"]
    preferred = []
    if local("state/work-order.json").exists():
        order = read("state/work-order.json")
        preferred = order.get("active_batch_ids", [])
        if order.get("mode") == "finish_existing_topics" and not order.get("opening_new_topics", False):
            allowed = set(order["started_topic_slugs"])
            topics = [t for t in topics if t["slug"] in allowed]
    in_scope = list(dict.fromkeys(a for t in topics for a in t["asset_ids"] if a in missing))
    return list(dict.fromkeys([a for a in preferred if a in in_scope] + in_scope))

def snapshot():
    files = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel == "state/integrity-manifest.json" or ".git" in p.relative_to(ROOT).parts or "__pycache__" in p.parts or p.suffix == ".tmp":
            continue
        assert p.resolve().is_relative_to(ROOT), f"External symlink: {rel}"
        files.append(dict(path=rel, bytes=p.stat().st_size, sha256=digest(p)))
    write_json("state/integrity-manifest.json", dict(updated_utc=now(), files=files,
               note="All paths are relative. Rebuild with refresh after intentional production changes."))
    return len(files)

def refresh():
    p, rows, topics, summary = inventory()
    by_id = {r["id"]: r for r in rows}
    slots = []
    for topic in p["topics"]:
        for aid in topic["asset_ids"]:
            r = by_id[aid]
            dest = None
            if r["status"] != "missing":
                category = "stickers" if r["status"] == "alpha_corners_clear" else "_needs-alpha"
                dest = f"delivery/{category}/{topic['slug']}/{aid}.png"
                copy_exact(local(r["source"]), local(dest))
            slots.append(dict(topic=topic["slug"], name_vi=topic["name_vi"], id=aid,
                              file=dest, status=r["status"], sha256=r.get("sha256"), review_note=r["review_note"]))
    expected_files = {s["file"] for s in slots if s["file"]}
    actual_files = {f.relative_to(ROOT).as_posix() for f in local("delivery").rglob("*.png")}
    assert actual_files == expected_files, "Stale delivery PNGs: archive superseded files under revisions before refresh"
    stamp = now()
    write_json("state/progress.json", dict(updated_utc=stamp, **summary, prompt_target_dimensions=[512,512],
               prompt_target_only=True, scripted_resizing=False, assets=rows, topics=topics, topic_slots=slots,
               alpha_note="Clear corner pixels are a technical check only; not approval of the cutout or artwork."))
    queue = ordered_missing(p, rows)
    write_json("state/generation-queue.json", dict(updated_utc=stamp, asset_ids=queue,
               rule="Missing masters in topic order, restricted by state/work-order.json when opening_new_topics is false. Shared IDs listed once."))
    write_json("state/resume.json", dict(updated_utc=stamp, workspace_root=".", **summary,
               next_asset_ids=queue[:16], next_action=("Continue with the first missing ID in state/generation-queue.json when generation is requested." if queue else "No missing masters in the current plan. Continue the open visual rework and game-scale QA in qa/visual-qa.json."),
               quota_note="Built-in image generation availability must be checked from a fresh tool response on continuation.",
               quality_work="Review qa/visual-qa.json candidates and game-scale silhouettes; clear alpha corners alone do not approve game integration."))
    write_json("qa/alpha-padding-audit.json", dict(updated_utc=stamp,
               padding_definition="Bounding box of all nonzero alpha pixels; read-only audit, no PNG edits.",
               assets=[dict(id=r["id"], **{k:r[k] for k in ("width","height","corner_alpha","padding_nonzero_alpha","review_edge","transparent_pixels","partial_alpha_pixels","opaque_pixels")}) for r in rows if r["status"] != "missing"]))
    csvfile = io.StringIO(newline="")
    writer = csv.DictWriter(csvfile, fieldnames=list(slots[0]))
    writer.writeheader(); writer.writerows(slots)
    write("delivery/topic-map.csv", csvfile.getvalue())
    render_gallery(p, rows, slots, summary)
    snapshot()
    return summary

def render_gallery(p, rows, slots, summary):
    esc = html.escape
    by_id = {r["id"]:r for r in rows}
    slot_files = {(r["topic"],r["id"]):r["file"] for r in slots}
    sections = []
    for t in p["topics"]:
        cards=[]
        for aid in t["asset_ids"]:
            r=by_id[aid]; f=slot_files[(t["slug"],aid)]
            status={"missing":"Chưa tạo", "needs_alpha":"Cần sửa nền", "alpha_corners_clear":"Có alpha ở góc · cần kiểm tra viền"}[r["status"]]
            graphic=f'<a href="{quote(f)}"><img loading="lazy" src="{quote(f)}" alt="{esc(r["subject"])}"></a>' if f else '<div class="placeholder">Chưa tạo</div>'
            dim=f'{r["width"]} × {r["height"]} px' if f else ''
            note=f'<p class="rework">Cần chỉnh: {esc(r["review_note"])}</p>' if r["review_note"] else ''
            cards.append(f'<figure data-status="{r["status"]}">{graphic}<figcaption>{esc(aid)}<small>{status}</small><small>{dim}</small>{note}</figcaption></figure>')
        count=sum(by_id[a]["status"] != "missing" for a in t["asset_ids"])
        search=esc(t["slug"]+' '+t["name_vi"]+' '+' '.join(t["asset_ids"]))
        sections.append(f'<section data-search="{search}"><h2>{esc(t["name_vi"])} <small>{count}/{p["target"]["slots_per_topic"]} hình</small></h2><div class="grid">{"".join(cards)}</div></section>')
    profiles=read("prompts/reference-profiles.json")
    refs=profiles["gallery_references"]
    reference_cards=''.join(f'<figure><img loading="lazy" src="{quote(r)}" alt="Mẫu phong cách gốc"><figcaption>{esc(Path(r).name)}</figcaption></figure>' for r in refs)
    template=local("scripts/gallery-template.html").read_text(encoding="utf-8")
    replacements={"TITLE":"stickers_production", "PRESENT":str(summary["generated_unique"]),
                  "TARGET_UNIQUE":str(summary["target_unique"]), "TARGET_TOPICS":str(summary["target_topics"]),
                  "SLOTS_PER_TOPIC":str(p["target"]["slots_per_topic"]),
                  "SHARED_COUNT":str(p["target"]["shared_assets"]),
                  "TOPICS":str(summary["topics_with_all_images"]), "ALPHA":str(summary["alpha_corners_clear_unique"]),
                  "OPAQUE":str(summary["needs_alpha_unique"]), "CARDS":''.join(sections), "REFERENCES":reference_cards}
    for key,value in replacements.items():
        template=template.replace('__'+key+'__',value)
    write("index.html",template)

def verify():
    manifest=read("state/integrity-manifest.json")
    errors=[]
    for f in manifest["files"]:
        path=local(f["path"])
        if not path.is_file() or path.stat().st_size != f["bytes"] or digest(path) != f["sha256"]:
            errors.append("Missing/changed: "+f["path"])
    known={f["path"] for f in manifest["files"]}
    actual={f.relative_to(ROOT).as_posix() for f in ROOT.rglob('*') if f.is_file() and '.git' not in f.relative_to(ROOT).parts and '__pycache__' not in f.parts and f.suffix != '.tmp'} - {"state/integrity-manifest.json"}
    for path in sorted(actual-known):
        errors.append("Untracked since snapshot: "+path)
    p, rows, topics, summary=inventory()
    progress=read("state/progress.json")
    for key,val in summary.items():
        if progress.get(key) != val: errors.append("Stale progress: "+key)
    if read("state/generation-queue.json")["asset_ids"] != ordered_missing(p,rows):
        errors.append("Stale generation queue")
    by_id={r["id"]:r for r in rows}
    for slot in progress["topic_slots"]:
        if slot["file"] and digest(local(slot["file"])) != by_id[slot["id"]].get("sha256"):
            errors.append("Delivery differs from master: "+slot["file"])
    for aid in read("state/generation-queue.json")["asset_ids"]:
        request_for(aid)
    for match in re.findall(r'(?:src|href)="([^"]+)"',local("index.html").read_text(encoding="utf-8")):
        from urllib.parse import unquote
        if not match.startswith(("#","https:","data:")) and not local(unquote(match)).is_file():
            errors.append("Broken gallery link: "+match)
    if errors:
        raise ValueError('\n'.join(errors[:40]))
    return dict(verified=True, manifest_files=len(known), **summary)

def save_asset(args):
    _, assets, _=plan()
    assert args.id in assets, "ID absent from plan"
    source=Path(args.source).expanduser().resolve()
    assert source.is_file(), "Image tool output missing"
    dest=local(f"masters/{args.id}.png")
    if dest.exists(): raise ValueError("Master already exists; review and archive the revision before replacement")
    request=read(args.request)
    assert request["id"] == args.id and request["target_dimensions"] == [512,512]
    for ref in request["referenced_image_paths"]: assert local(ref).is_file()
    info=png_info(source)
    copy_exact(source,dest)
    log=dict(created_utc=now(),id=args.id,request=args.request,result_file=f"masters/{args.id}.png",
             source_sha256=digest(source),visual_review="pending",**info)
    logfile=local("logs/generation.jsonl"); logfile.parent.mkdir(parents=True,exist_ok=True)
    with logfile.open("a",encoding="utf-8") as out: out.write(json.dumps(log,ensure_ascii=False)+'\n')
    return refresh()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    for command in ("status","refresh","verify"): sub.add_parser(command)
    nxt=sub.add_parser("next"); nxt.add_argument("--count",type=int,default=1); nxt.add_argument("--write",action="store_true")
    save=sub.add_parser("save"); save.add_argument("--id",required=True); save.add_argument("--source",required=True); save.add_argument("--request",required=True)
    args=parser.parse_args()
    if args.command == "status": result=inventory()[3]
    elif args.command == "refresh": result=refresh()
    elif args.command == "verify": result=verify()
    elif args.command == "save": result=save_asset(args)
    else:
        assert 1 <= args.count <= 32, "Choose 1 to 32 requests"
        p,rows,_,_=inventory()
        result=[request_for(aid) for aid in ordered_missing(p,rows)[:args.count]]
        if args.write:
            for request in result:
                filename=f'state/requests/{request["id"]}.json'
                if local(filename).exists() and read(filename) != request:
                    raise ValueError("A different saved request exists: "+filename)
                write_json(filename,request)
            snapshot()
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ERROR: {error}",file=sys.stderr)
        sys.exit(1)
