W = 250
H = 122

_LBL_HR_Y = 1
_GRID_TOP = 11
_BL = 61
_GRID_BOT = 110
_LBL_MN_Y = 113

_X0 = 8
_X1 = 242
_XR = _X1 - _X0

_ECG_HW = 22
_PK = 42

_ECG = [
    (-1.00, 0.00),
    (-0.75, 0.00),
    (-0.62, 0.08),
    (-0.50, 0.15),
    (-0.38, 0.08),
    (-0.29, 0.00),
    (-0.21, 0.00),
    (-0.12, -0.10),
    (-0.04, 0.20),
    (0.00, 1.00),
    (0.04, 0.15),
    (0.08, -0.18),
    (0.17, -0.03),
    (0.25, 0.00),
    (0.37, 0.05),
    (0.50, 0.22),
    (0.62, 0.05),
    (0.75, 0.00),
    (1.00, 0.00),
]


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


def _grid(fb, yt, yb):
    for y in range(yt, yb + 1, 5):
        for x in range(0, W, 5):
            fb.pixel(x, y, 0)
    for x in range(0, W, 25):
        for y in range(yt, yb + 1):
            if y & 1 == 0:
                fb.pixel(x, y, 0)
    for y in range(yt, yb + 1, 25):
        for x in range(0, W):
            if x & 1 == 0:
                fb.pixel(x, y, 0)


def _trace(fb, bl, px, pk, sign):
    prev = bl
    for x in range(W):
        d = x - px
        if -_ECG_HW <= d <= _ECG_HW:
            off = round(_amp(d / _ECG_HW) * pk)
        else:
            off = 0
        y = bl + sign * off
        y0 = min(prev, y)
        y1 = max(prev, y) + 1
        for fy in range(max(0, y0), min(y1 + 1, H)):
            fb.pixel(x, fy, 0)
        prev = y


def _label(fb, val, cx, y, hl=False):
    s = str(val)
    tw = len(s) * 8
    tx = cx - tw // 2
    if hl:
        fb.fill_rect(max(tx - 2, 0), y - 1, tw + 4, 11, 0)
        fb.text(s, max(tx, 0), y, 1)
    else:
        fb.text(s, max(tx, 0), y, 0)


def draw_watchface(fb, hour12, minute, is_pm):
    fb.fill(1)

    for h in range(1, 13):
        _label(fb, h, _hx(h), _LBL_HR_Y, h == hour12)

    _grid(fb, _GRID_TOP, _GRID_BOT)

    _trace(fb, _BL, _hx(hour12), _PK, -1)
    _trace(fb, _BL, _mx(minute), _PK, 1)

    near5 = ((minute + 2) // 5) * 5
    if near5 >= 60:
        near5 = 55
    for m in range(0, 60, 5):
        _label(fb, m, _mx(m), _LBL_MN_Y, m == near5)

    fb.text("PM" if is_pm else "AM", 234, _LBL_MN_Y, 0)
