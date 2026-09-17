from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    'tailor-dress-form-v1.png', 'terrarium-mister-v1.png',
    'terrarium-moss-v1.png', 'snorkel-mask-v1.png',
    'snorkel-tube-v1.png', 'dive-rashguard-v1.png',
    'table-coral-v3.png', 'coral-nursery-tree-v1.png',
    'calligraphy-inkstone-v2.png', 'bongos-v1.png',
    'marching-trumpet-v1.png', 'dragonfly-v1.png',
]
base = ROOT / 'revisions/rework-20260917'
for start in (0, 6):
    canvas = Image.new('RGB', (1200, 1840), '#2b3038')
    draw = ImageDraw.Draw(canvas)
    for i, name in enumerate(FILES[start:start+6]):
        im = Image.open(base / name).convert('RGBA')
        a = np.asarray(im)[:, :, 3]
        ys, xs = np.where(a >= 128)
        pad = (int(xs.min()), int(im.width-1-xs.max()), int(ys.min()), int(im.height-1-ys.max()))
        print(name, im.size, 'pad128', pad, 'edge alpha', int(np.count_nonzero(a[0]))+int(np.count_nonzero(a[-1]))+int(np.count_nonzero(a[:,0]))+int(np.count_nonzero(a[:,-1])))
        tile = im.copy()
        tile.thumbnail((555, 555))
        x = (i % 2) * 600 + (600-tile.width)//2
        y = (i // 2) * 610 + (570-tile.height)//2
        canvas.paste(tile, (x, y), tile)
        draw.text(((i % 2)*600+10, (i//2)*610+570), name, fill='white')
    out = ROOT / f'qa/rework-20260917/candidates-dark-{start//6+1}.png'
    canvas.save(out)
    print(out)
