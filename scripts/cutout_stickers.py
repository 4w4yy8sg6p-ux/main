"""Вырезает стикеры из assets/stickers-src/*.jpg (белый фон) в прозрачные PNG
с ровной белой обводкой: public/stickers/<name>.png."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SRC = Path("assets/stickers-src")
DST = Path("public/stickers")
# У «фото»-стикера фон с серым шумом: объект ищем по насыщенности цвета
BY_SATURATION = {"smile"}
BORDER = 11  # толщина собственной белой обводки, px


def disk(r):
    y, x = np.ogrid[-r : r + 1, -r : r + 1]
    return x * x + y * y <= r * r


def cutout(path: Path) -> Image.Image:
    name = path.stem
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    pad = BORDER + 4  # запас, чтобы обводка не упиралась в край картинки
    rgb = np.pad(rgb, ((pad, pad), (pad, pad), (0, 0)), constant_values=255)
    if name in BY_SATURATION:
        sat = rgb.max(2) - rgb.min(2)
        mask = ndi.binary_opening(sat > 28, disk(2))
        mask = ndi.binary_closing(mask, disk(8))
    else:
        mask = ndi.binary_closing(rgb.min(2) < 238, disk(2))
    labels, n = ndi.label(mask)
    sizes = ndi.sum(mask, labels, range(1, n + 1))
    obj = labels == (1 + int(np.argmax(sizes)))
    obj = ndi.binary_fill_holes(obj)
    if name in BY_SATURATION:
        obj = ndi.binary_dilation(obj, disk(2))  # захватываем тёмный контур
    outline = ndi.binary_dilation(obj, disk(BORDER))

    out = rgb.copy()
    out[outline & ~obj] = 255  # ровная белая обводка
    alpha = Image.fromarray((outline * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    im = Image.fromarray(out.astype(np.uint8)).convert("RGBA")
    im.putalpha(alpha)
    return im.crop(im.getbbox())


if __name__ == "__main__":
    DST.mkdir(parents=True, exist_ok=True)
    for p in sorted(SRC.glob("*.jpg")):
        im = cutout(p)
        im.save(DST / f"{p.stem}.png", optimize=True)
        print(p.stem, im.size)
