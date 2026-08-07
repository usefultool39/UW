import json
import os
from PIL import Image

d = r"C:\Users\liang\Desktop\UW\materials\inbox\visual\characters"
for f in sorted(os.listdir(d)):
    if f.endswith(".png") and "v003" in f:
        p = os.path.join(d, f)
        im = Image.open(p)
        print(f"{f}: {im.size} {im.mode}")
        # 检查每 64x96 帧的 alpha nonzero
        a = im.split()[-1]
        for r in range(4):
            for c in range(12):
                box = (c * 64, r * 96, (c + 1) * 64, (r + 1) * 96)
                crop = a.crop(box)
                extrema = crop.getextrema()
                nonzero = sum(1 for px in crop.getdata() if px > 0)
                if nonzero == 0:
                    print(f"  row{r} col{c}: EMPTY!")
