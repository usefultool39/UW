import os
from PIL import Image

d = r"C:\Users\liang\Desktop\UW\materials\inbox\visual\world"
for f in sorted(os.listdir(d)):
    if f.endswith(".png") and "v003" in f:
        p = os.path.join(d, f)
        im = Image.open(p)
        size = im.size
        mode = im.mode
        # alpha stats
        if mode == "RGBA":
            a = im.split()[-1]
            extrema = a.getextrema()
            nonzero = sum(1 for px in a.getdata() if px > 0)
            total = a.size[0] * a.size[1]
            print(f"{f}: {size} {mode}  alpha=[{extrema[0]},{extrema[1]}] nonzero={nonzero}/{total} ({100*nonzero/total:.1f}%)")
        else:
            print(f"{f}: {size} {mode}")
