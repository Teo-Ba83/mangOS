#!/usr/bin/python3
"""Builds the MangOS logo files from the artwork mangos-logo-full-source.png
(mango + "MangOS" wordmark, transparent background). Run once after changing
the artwork; the results are committed and used by make-logo.sh:
  mangos-logo.svg               the mango alone (colour), square
  mangos-logo-full.png          mango + wordmark, trimmed
  mangos-logo-mono-dark.svg     one-colour silhouettes for the top bar
  mangos-logo-mono-light.svg
  mangos-logo-symbolic.svg
The SVGs embed PNG images, so every tool that reads the old vector logo
(rsvg-convert, GTK, the GRUB splash composition in build.sh) keeps working."""
import base64, io, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
src = Image.open(os.path.join(HERE, "mangos-logo-full-source.png")).convert("RGBA")
a = src.getchannel("A")
w, h = src.size

# the mango is above an empty band of rows that separates it from the wordmark
rows = [any(a.getpixel((x, y)) > 40 for x in range(0, w, 2)) for y in range(h)]
y = int(h * 0.55)
while y < h and rows[y]:
    y += 1
mango = src.crop((0, 0, w, y))
mango = mango.crop(mango.getchannel("A").getbbox())
src.crop(a.getbbox()).save(os.path.join(HERE, "mangos-logo-full.png"), optimize=True)


def square(im, size, margin=0.04):
    side = int(max(im.size) * (1 + 2 * margin))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    return canvas.resize((size, size), Image.LANCZOS)


def svg(im, title="MangOS"):
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
    data = base64.b64encode(buf.getvalue()).decode()
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'viewBox="0 0 512 512" width="512" height="512">\n'
            f'  <title>{title}</title>\n  <defs></defs>\n'
            f'  <image xmlns:xlink="http://www.w3.org/1999/xlink" x="0" y="0" width="512" height="512" xlink:href="data:image/png;base64,{data}"/>\n'
            '</svg>\n')


color = square(mango, 512)
open(os.path.join(HERE, "mangos-logo.svg"), "w").write(svg(color))


def mono(rgb, size=256):
    """One colour; the artwork's dark outlines become thin gaps, so leaf,
    stem, fruit and bite stay readable at top-bar size."""
    big = square(mango, 1024)
    lum = big.convert("L")
    alpha = big.getchannel("A")
    cut = Image.eval(lum, lambda v: 0 if v < 70 else 255)
    from PIL import ImageChops, ImageFilter
    shape = ImageChops.multiply(alpha.point(lambda v: 255 if v > 110 else 0), cut)
    shape = shape.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    shape = shape.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), rgb + (0,))
    out.putalpha(shape)
    return out


for name, rgb in (("mono-dark", (0x1D, 0x1D, 0x1F)), ("mono-light", (0xFF, 0xFF, 0xFF)),
                  ("symbolic", (0xBE, 0xBE, 0xBE))):
    open(os.path.join(HERE, f"mangos-logo-{name}.svg"), "w").write(svg(mono(rgb)))
print("logo files written")

# Mango Store app icon: the mango on a rounded teal square.
from PIL import ImageDraw
S = 1024
bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
grad = Image.new("RGBA", (S, S))
top, bottom = (0x2E, 0xD3, 0xB7), (0x0B, 0x72, 0x86)
gd = ImageDraw.Draw(grad)
for yy in range(S):
    t = yy / (S - 1)
    gd.line([(0, yy), (S, yy)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,))
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle([48, 48, S - 48, S - 48], radius=210, fill=255)
bg.paste(grad, (0, 0), mask)
fruit = square(mango, 700, margin=0.02)
shadow = Image.new("RGBA", fruit.size, (0, 0, 0, 0))
shadow.putalpha(fruit.getchannel("A").point(lambda v: v * 0.35))
from PIL import ImageFilter as _F
bg.alpha_composite(shadow.filter(_F.GaussianBlur(18)), ((S - 700) // 2 + 6, (S - 700) // 2 + 22))
bg.alpha_composite(fruit, ((S - 700) // 2, (S - 700) // 2))
open(os.path.join(HERE, "mangos-store.svg"), "w").write(svg(bg.resize((512, 512), Image.LANCZOS), "Mango Store"))
print("store icon written")
