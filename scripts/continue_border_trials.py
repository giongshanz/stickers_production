"""Resume a small reviewed border batch from immutable local RGB snapshots."""
import argparse,sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
sys.dont_write_bytecode=True
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--deps',required=True)
a=p.parse_args();sys.path.insert(0,a.deps)
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from border_geometry import cutout,summarize

ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'qa/border-continuation-20260916'
OUT=ROOT/'revisions/border-continuation-20260916'
CONFIG={
 'beehive-skep':{'radius':43.2,'holes':[],'repair_white':True},
 'honey-lemon-tea':{'radius':30.1,'holes':[(1000,600)],'repair_white':True},
 'honey-butter-dish':{'radius':None,'holes':[],'repair_white':False},
 'honey-pancakes':{'radius':None,'holes':[],'repair_white':False},
}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def comp(im,color):
 bg=Image.new('RGBA',im.size,(*color,255));bg.alpha_composite(im);return bg.convert('RGB')
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 reports=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
 for aid,config in CONFIG.items():
  source=OUT/'sources'/f'{aid}.png';raw=np.array(Image.open(source).convert('RGB'))
  mask_path=QA/f'{aid}-paper-input.png'
  if not mask_path.exists():
   im=Image.open(ROOT/f'revisions/alpha-audit-20260916/{aid}-candidate.png').convert('RGBA')
   im.getchannel('A').save(mask_path)
  paper=ndi.binary_fill_holes(np.array(Image.open(mask_path))>=128)
  radius=config['radius'] or 20.
  rgba,protected,dist,geometry=cutout(raw,paper,radius,config['holes'])
  if config['radius'] is None:
   edge=paper&~ndi.binary_erosion(paper)
   widths=dist[edge];widths=widths[(widths>8)&(widths<70)]
   measured=float(np.median(widths))
   # Strict alpha-only: keep the cut within clean white RGB of the source.
   neutral=(np.ptp(raw.astype(np.int16),axis=2)<=18)
   dirty=~protected&neutral&(raw.min(axis=2)<230)&(dist>6)&(dist<measured+5)
   limit=float(dist[dirty].min())-1 if dirty.any() else measured-1
   radius=round(min(measured-1,limit),1)
   assert radius>8 and radius>measured*.6,(aid,measured,radius)
   rgba,protected,dist,geometry=cutout(raw,paper,radius,config['holes'])
   geometry['measured_source_width_px']=measured
   geometry['alpha_only_inset_px']=measured-radius
  if not config['repair_white']:rgba[:,:,:3]=raw
  changed=np.any(rgba[:,:,:3]!=raw,axis=2)
  assert not (changed&protected).any()
  if not config['repair_white']:assert not changed.any()
  assert not rgba[[0,-1],:,3].any() and not rgba[:,[0,-1],3].any()
  candidate=OUT/f'{aid}.png';result=Image.fromarray(rgba);result.save(candidate)
  for name,color in [('dark',(30,32,48)),('light',(244,242,237)),('green',(60,125,99))]:
   comp(result,color).save(QA/f'{aid}-{name}.png')
  board=Image.new('RGB',(1400,740),(30,32,48));draw=ImageDraw.Draw(board)
  for i,(label,im) in enumerate([('ANH GOC',Image.fromarray(raw)),('BAN XOA NEN',comp(result,(30,32,48)))]):
   thumb=im.copy();thumb.thumbnail((670,670),Image.Resampling.LANCZOS);board.paste(thumb,(i*700+15,50));draw.text((i*700+20,15),label,font=font,fill='white')
  board.save(QA/f'{aid}-comparison.png')
  Image.fromarray(protected.astype('uint8')*255).save(QA/f'{aid}-protected.png')
  mask=rgba[:,:,3]>=128;edge=mask&~ndi.binary_erosion(mask)
  record=dict(id=aid,created_utc=datetime.now(timezone.utc).isoformat(),source=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),
   candidate=candidate.relative_to(ROOT).as_posix(),candidate_sha256=sha(candidate),paper_input=mask_path.relative_to(ROOT).as_posix(),
   dimensions=list(result.size),dimensions_unchanged=True,alpha_only=not config['repair_white'],rgb_unchanged=not changed.any(),
   painted_rgb_unchanged=True,protected_pixels=int(protected.sum()),rgb_changed_pixels=int(changed.sum()),
   radius_px=radius,holes_xy=config['holes'],widths_px=summarize(dist[edge]),geometry=geometry,status='pending_visual_review')
  record['rgb_unchanged']=bool(record['rgb_unchanged'])
  if aid=='beehive-skep':
   assert protected.sum()==802540
   record['previous_approved_sha256']='81221a363148092b9942ea9289b8a6afda462fe3ffefeaebdce0d6593afa14fc'
   record['matches_previous_approved_bytes']=record['candidate_sha256']==record['previous_approved_sha256']
  if aid=='honey-lemon-tea':assert rgba[600,1000,3]==0
  write(QA/f'{aid}.json',record);reports.append(record)
  print(json.dumps({k:record[k] for k in ['id','radius_px','rgb_unchanged','protected_pixels','candidate_sha256']},ensure_ascii=False),flush=True)
 write(QA/'report.json',reports)
if __name__=='__main__':main()
