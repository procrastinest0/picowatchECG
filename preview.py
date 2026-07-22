"""Desktop preview renderer. Not deployed to the Pico.

Usage: python preview.py [hour24] [minute]          # static PNG
       python preview.py [hour24] [minute] --sweep   # animated GIF
"""
import sys
from PIL import Image, ImageDraw

W, H = 250, 122

_LBL_HR_Y = 1
_GRID_TOP = 11
_BL = 61
_GRID_BOT = 110
_LBL_MN_Y = 113
_X0, _X1 = 8, 242
_XR = _X1 - _X0
_ECG_HW = 22
_PK = 42
SWEEP_STEPS = 20

_ECG = [
    (-1.00, 0.00), (-0.75, 0.00), (-0.62, 0.08), (-0.50, 0.15),
    (-0.38, 0.08), (-0.29, 0.00), (-0.21, 0.00), (-0.12, -0.10),
    (-0.04, 0.20), (0.00, 1.00),  (0.04, 0.15),  (0.08, -0.18),
    (0.17, -0.03), (0.25, 0.00),  (0.37, 0.05),  (0.50, 0.22),
    (0.62, 0.05),  (0.75, 0.00),  (1.00, 0.00),
]

_FONT = {
    ' ': [0x00]*8,
    '0': [0x3C,0x66,0x6E,0x7E,0x76,0x66,0x3C,0x00],
    '1': [0x18,0x38,0x18,0x18,0x18,0x18,0x7E,0x00],
    '2': [0x3C,0x66,0x06,0x1C,0x30,0x66,0x7E,0x00],
    '3': [0x3C,0x66,0x06,0x1C,0x06,0x66,0x3C,0x00],
    '4': [0x0C,0x1C,0x3C,0x6C,0x7E,0x0C,0x0C,0x00],
    '5': [0x7E,0x60,0x7C,0x06,0x06,0x66,0x3C,0x00],
    '6': [0x1C,0x30,0x60,0x7C,0x66,0x66,0x3C,0x00],
    '7': [0x7E,0x66,0x06,0x0C,0x18,0x18,0x18,0x00],
    '8': [0x3C,0x66,0x66,0x3C,0x66,0x66,0x3C,0x00],
    '9': [0x3C,0x66,0x66,0x3E,0x06,0x0C,0x38,0x00],
    'A': [0x18,0x3C,0x66,0x66,0x7E,0x66,0x66,0x00],
    'M': [0x63,0x77,0x7F,0x6B,0x63,0x63,0x63,0x00],
    'P': [0x7C,0x66,0x66,0x7C,0x60,0x60,0x60,0x00],
}


def _hx(h):
    return _X0 + (h - 1) * _XR // 11

def _mx(m):
    return _X0 + m * _XR // 59 if m else _X0

def _amp(t):
    if t <= -1.0 or t >= 1.0:
        return 0.0
    for i in range(len(_ECG) - 1):
        t0, a0 = _ECG[i]
        t1, a1 = _ECG[i + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 != t0 else 0.0
            return a0 + f * (a1 - a0)
    return 0.0


def render(hour24, minute, sweep_x=W):
    h12 = hour24 % 12 or 12
    pm = hour24 >= 12

    scale = 4
    sw, sh = W * scale, H * scale
    img = Image.new("RGB", (sw, sh), (245, 245, 240))
    draw = ImageDraw.Draw(img)

    def px(x, y, c=(0, 0, 0)):
        if 0 <= x < W and 0 <= y < H:
            x0, y0 = x * scale, y * scale
            draw.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill=c)

    def text(s, x, y, inv=False):
        for ci, ch in enumerate(s):
            cx = x + ci * 8
            bitmap = _FONT.get(ch, [0]*8)
            for row in range(8):
                for col in range(8):
                    if bitmap[row] & (1 << (7 - col)):
                        px(cx + col, y + row,
                           (255, 255, 255) if inv else (0, 0, 0))
                    elif inv:
                        px(cx + col, y + row, (0, 0, 0))

    def fill_rect(x, y, w, h, c):
        for dy in range(h):
            for dx in range(w):
                px(x + dx, y + dy, c)

    # grid
    gc = (180, 180, 175)
    gb = (140, 140, 135)
    for y in range(_GRID_TOP, _GRID_BOT + 1, 5):
        for x in range(0, W, 5):
            px(x, y, gc)
    for x in range(0, W, 25):
        for y in range(_GRID_TOP, _GRID_BOT + 1):
            if y & 1 == 0:
                px(x, y, gb)
    for y in range(_GRID_TOP, _GRID_BOT + 1, 25):
        for x in range(0, W):
            if x & 1 == 0:
                px(x, y, gb)

    # traces (clipped to sweep_x)
    tc = (10, 10, 10)
    hr_px = _hx(h12)
    mn_px = _mx(minute)
    for peak_x, sign in [(hr_px, -1), (mn_px, 1)]:
        prev = _BL
        for x in range(min(sweep_x, W)):
            d = x - peak_x
            if -_ECG_HW <= d <= _ECG_HW:
                off = round(_amp(d / _ECG_HW) * _PK)
            else:
                off = 0
            y = _BL + sign * off
            y0, y1 = min(prev, y), max(prev, y) + 1
            for fy in range(max(0, y0), min(y1 + 1, H)):
                px(x, fy, tc)
            prev = y

    # sweep cursor
    if 0 < sweep_x < W:
        for y in range(_GRID_TOP, _GRID_BOT + 1):
            if y % 3 != 0:
                px(sweep_x, y, (60, 60, 60))

    # hour labels
    for h in range(1, 13):
        s = str(h)
        tw = len(s) * 8
        tx = _hx(h) - tw // 2
        if h == h12:
            fill_rect(max(tx - 2, 0), _LBL_HR_Y - 1, tw + 4, 11, (0, 0, 0))
            text(s, max(tx, 0), _LBL_HR_Y, inv=True)
        else:
            text(s, max(tx, 0), _LBL_HR_Y)

    # minute labels
    near5 = ((minute + 2) // 5) * 5
    if near5 >= 60:
        near5 = 55
    for m in range(0, 60, 5):
        s = str(m)
        tw = len(s) * 8
        tx = _mx(m) - tw // 2
        if m == near5:
            fill_rect(max(tx - 2, 0), _LBL_MN_Y - 1, tw + 4, 11, (0, 0, 0))
            text(s, max(tx, 0), _LBL_MN_Y, inv=True)
        else:
            text(s, max(tx, 0), _LBL_MN_Y)

    text("PM" if pm else "AM", 234, _LBL_MN_Y)

    return img


def render_sweep_gif(hour24, minute, filename="sweep.gif"):
    step_w = (W + SWEEP_STEPS - 1) // SWEEP_STEPS
    frames = []
    for step in range(SWEEP_STEPS + 1):
        sx = min(step * step_w, W)
        frames.append(render(hour24, minute, sweep_x=sx))
    frames.append(render(hour24, minute))
    frames[0].save(
        filename, save_all=True, append_images=frames[1:],
        duration=150, loop=0,
    )
    return len(frames)


if __name__ == "__main__":
    h = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    m = int(sys.argv[2]) if len(sys.argv) > 2 else 23
    sweep = "--sweep" in sys.argv

    if sweep:
        n = render_sweep_gif(h, m)
        print(f"Saved sweep.gif  ({h:02d}:{m:02d}, {n} frames)")
    else:
        img = render(h, m)
        img.save("preview.png")
        print(f"Saved preview.png  ({h:02d}:{m:02d}, {'PM' if h>=12 else 'AM'})")
