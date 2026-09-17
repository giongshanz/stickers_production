#!/usr/bin/env python3
"""Portable, non-destructive alpha audit. Never edits RGB or resizes masters."""
import json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import alpha_cleanup as base
ROOT=Path(__file__).resolve().parent.parent
RUN='alpha-audit-20260916'
OUT=ROOT/'revisions'/RUN
QA=ROOT/'qa'/RUN
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write(p,d):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def components(mask):
 # Run-length connected components, eight-neighbour adjacency.
 h,w=mask.shape;parent=[0];rank=[0];runs=[];prev=[]
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 def join(a,b):
  a=find(a);b=find(b)
  if a==b:return
  if rank[a]<rank[b]:a,b=b,a
  parent[b]=a
  if rank[a]==rank[b]:rank[a]+=1
 for y in range(h):
  row=mask[y];starts=np.flatnonzero(row&~np.r_[False,row[:-1]]);ends=np.flatnonzero(row&~np.r_[row[1:],False])+1
  current=[];pi=0
  for left,right in zip(starts.tolist(),ends.tolist()):
   label=len(parent);parent.append(label);rank.append(0)
   while pi<len(prev) and prev[pi][1]<left:pi+=1
   j=pi
   while j<len(prev) and prev[j][0]<=right:
    join(label,prev[j][2]);j+=1
   current.append((left,right,label));runs.append((y,left,right,label))
  prev=current
 roots=np.array([find(i) for i in range(len(parent))],dtype=np.int32)
 labels=np.zeros((h,w),np.int32)
 for y,left,right,label in runs:labels[y,left:right]=roots[label]
 counts=np.bincount(labels.ravel(),minlength=len(parent));counts[0]=0
 return labels,counts
def preview(aid,rgba,suffix='candidate'):
 im=Image.fromarray(rgba)
 for name,color in [('dark',(40,47,58,255)),('light',(250,232,198,255))]:
  bg=Image.new('RGBA',im.size,color);bg.alpha_composite(im)
  p=QA/(aid+'-'+suffix+'-'+name+'.png');p.parent.mkdir(parents=True,exist_ok=True);bg.convert('RGB').save(p)
def run():
 OUT.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
 progress=read('state/progress.json');reports=[]
 for item in progress['assets']:
  if item['status']=='missing':continue
  aid=item['id'];src=ROOT/item['source']
  with Image.open(src) as im:arr=np.asarray(im.convert('RGBA')).copy();size=im.size
  rgb=arr[:,:,:3];alpha=arr[:,:,3].copy();opaque=np.all(alpha==255)
  old_candidate=ROOT/'revisions/background-cleanup-20260915'/(aid+'-alpha.png')
  if opaque:
   if old_candidate.exists() and read(str(old_candidate.with_suffix('.json').relative_to(ROOT)))['source_sha256']==digest(src):
    alpha=np.asarray(Image.open(old_candidate).convert('RGBA'))[:,:,3].copy()
   else:
    lo=rgb.min(2);hi=rgb.max(2);white=(lo>=242)&(hi.astype(int)-lo<=16)
    mask=~base.exterior(~white)
    labels,areas=components(mask);chosen=int(areas.argmax())
    primary=labels==chosen
    assert .015<primary.mean()<.95,(aid,float(primary.mean()))
    alpha=np.asarray(Image.fromarray(primary.astype('uint8')*255).filter(ImageFilter.GaussianBlur(.45))).copy();alpha[~primary]=0
  labels,areas=components(alpha>8)
  lo=rgb.min(2);hi=rgb.max(2);chroma=hi.astype(int)-lo
  colored=(chroma>24)&(hi>45)&(alpha>8)
  color_counts=np.bincount(labels.ravel(),weights=colored.ravel(),minlength=len(areas))
  remove=[int(i) for i in np.flatnonzero(areas) if (areas[i]<50 and color_counts[i]<4) or (areas[i]<2500 and color_counts[i]==0)]
  if remove:alpha[np.isin(labels,remove)]=0
  result=np.dstack([rgb,alpha])
  out=OUT/(aid+'-candidate.png');Image.fromarray(result).save(out)
  assert np.array_equal(np.asarray(Image.open(out))[:,:,:3],rgb)
  preview(aid,result)
  r=dict(id=aid,source=item['source'],source_sha256=digest(src),candidate=out.relative_to(ROOT).as_posix(),
   candidate_sha256=digest(out),dimensions=list(size),rgb_unchanged=True,was_opaque=bool(opaque),
   removed_detached_components=len(remove),removed_component_pixels=int(sum(areas[i] for i in remove)),status='needs_visual_audit',holes=[],notes=[])
  reports.append(r)
  if len(reports)%10==0:print('Audited',len(reports),flush=True)
 write('qa/'+RUN+'/audit.json',reports)
 sheets(reports)
 print('Done',len(reports),flush=True)
def sheets(reports,suffix='candidate'):
 for page in range((len(reports)+11)//12):
  sheet=Image.new('RGB',(1440,1170),(40,47,58));d=ImageDraw.Draw(sheet)
  for n,r in enumerate(reports[page*12:page*12+12]):
   im=Image.open(QA/(r['id']+'-'+suffix+'-dark.png'));im.thumbnail((340,340))
   x=(n%4)*360+(360-im.width)//2;y=(n//4)*390+10
   sheet.paste(im,(x,y));d.text(((n%4)*360+8,(n//4)*390+359),r['id'],fill='white')
   d.text(((n%4)*360+8,(n//4)*390+374),('opaque source' if r['was_opaque'] else 'alpha source')+' | flecks '+str(r['removed_detached_components']),fill='#adc4db')
  sheet.save(QA/(suffix+'-sheet-'+str(page+1)+'.jpg'),quality=92)
if __name__=='__main__':run()
