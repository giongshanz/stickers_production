#!/usr/bin/env python3
"""User-authorized alpha cleanup. RGB bytes and canvas dimensions are invariant."""
import argparse, json, sys, hashlib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageFilter
ROOT=Path(__file__).resolve().parent.parent
RUN="revisions/background-cleanup-20260915"

def sha(path):
    with open(path,"rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()
def save_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def connected(passable,seeds):
    """Four-connected scanline flood; no third-party segmentation runtime."""
    h,w=passable.shape
    seen=np.zeros((h,w),dtype=bool)
    stack=list(seeds)
    while stack:
        x,y=stack.pop()
        if not passable[y,x] or seen[y,x]: continue
        row=passable[y] & ~seen[y]
        left_false=np.flatnonzero(~row[:x])
        right_false=np.flatnonzero(~row[x+1:])
        left=int(left_false[-1]+1) if len(left_false) else 0
        right=int(x+1+right_false[0]) if len(right_false) else w
        seen[y,left:right]=True
        for yy in (y-1,y+1):
            if yy<0 or yy>=h: continue
            line=passable[yy,left:right] & ~seen[yy,left:right]
            starts=np.flatnonzero(line & ~np.r_[False,line[:-1]])
            stack.extend((int(left+i),yy) for i in starts)
    return seen

def exterior(passable):
    h,w=passable.shape
    seeds=[(x,y) for y in (0,h-1) for x in range(w) if passable[y,x]]
    seeds.extend((x,y) for x in (0,w-1) for y in range(1,h-1) if passable[y,x])
    return connected(passable,seeds)

def cleanup(aid,source_relative=None,erode=0):
    source=ROOT/(source_relative or f"masters/{aid}.png")
    with Image.open(source) as im:
        rgb=np.asarray(im.convert("RGB")).copy()
        size=im.size
    lo=rgb.min(axis=2); hi=rgb.max(axis=2)
    white=(lo>=242)&((hi.astype(int)-lo)<=16)
    border=np.concatenate([white[0],white[-1],white[:,0],white[:,-1]])
    if erode:
        white=np.asarray(Image.fromarray(white.astype("uint8")*255).filter(ImageFilter.MinFilter(2*erode+1)))>0
    bg=exterior(~white)
    candidate=~bg
    h,w=candidate.shape
    ys,xs=np.nonzero(candidate)
    if len(xs)==0: raise ValueError("No enclosed sticker detected")
    index=np.argmin((xs-w/2)**2+(ys-h/2)**2)
    primary=connected(candidate,[(int(xs[index]),int(ys[index]))])
    fraction=float(primary.mean())
    if not .025<fraction<.94: raise ValueError(f"Unsafe mask fraction {fraction:.4f}; manual review required")
    if erode:
        expanded=np.asarray(Image.fromarray(primary.astype("uint8")*255).filter(ImageFilter.MaxFilter(2*erode+1)))>0
        primary=primary | (expanded & (lo>=229) & ((hi.astype(int)-lo)<=18))
    # Feather inward only: no formerly discarded checker pixel acquires alpha.
    alpha=np.asarray(Image.fromarray(primary.astype("uint8")*255).filter(ImageFilter.GaussianBlur(.45))).copy()
    alpha[~primary]=0
    rgba=np.dstack([rgb,alpha])
    destination=ROOT/RUN/(aid+"-alpha.png")
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():
        previous=json.loads(destination.with_suffix(".json").read_text(encoding="utf-8"))
        if previous["source_sha256"]!=sha(source): raise ValueError("Source changed since candidate generation")
        return previous
    Image.fromarray(rgba).save(destination)
    with Image.open(destination) as check:
        out=np.asarray(check)
        assert check.size==size and np.array_equal(out[:,:,:3],rgb), "RGB/dimensions changed"
        assert all(out[y,x,3]==0 for x,y in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))), "Corners not transparent"
    report=dict(id=aid,created_utc=datetime.now(timezone.utc).isoformat(),
        source=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),
        candidate=destination.relative_to(ROOT).as_posix(),candidate_sha256=sha(destination),
        dimensions=list(size),rgb_unchanged=True,dimensions_unchanged=True,
        alpha_only=True,transparent_pixels=int((alpha==0).sum()),opaque_pixels=int((alpha==255).sum()),
        partial_alpha_pixels=int(((alpha>0)&(alpha<255)).sum()),foreground_fraction=fraction,
        source_border_white_fraction=float(border.mean()),white_barrier_erosion=erode,
        status="pending_visual_review",note="Exterior removal only; inspect enclosed openings, border and fine parts before promotion.")
    save_json(destination.with_suffix(".json"),report)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ids",nargs="*")
    parser.add_argument("--all-opaque",action="store_true")
    parser.add_argument("--source")
    parser.add_argument("--erode",type=int,default=0)
    args=parser.parse_args()
    ids=args.ids
    if args.all_opaque:
        progress=json.loads((ROOT/"state/progress.json").read_text(encoding="utf-8"))
        ids=[a["id"] for a in progress["assets"] if a["status"]=="needs_alpha"]
    results=[]
    for aid in ids:
        try:
            result=cleanup(aid,args.source,args.erode)
        except Exception as e:
            result=dict(id=aid,error=str(e),status="needs_manual_review")
        results.append(result)
        print(json.dumps(result,ensure_ascii=False),flush=True)
    save_json(ROOT/RUN/"latest-run.json",results)
if __name__=="__main__": main()
