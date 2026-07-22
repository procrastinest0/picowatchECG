import framebuf
import time
from machine import Pin


def _build_reverse_table():
    t = bytearray(256)
    for i in range(256):
        v, r = i, 0
        for _ in range(8):
            r = (r << 1) | (v & 1)
            v >>= 1
        t[i] = r
    return bytes(t)

_REV = _build_reverse_table()


class EPD_2in13_V4:
    """Waveshare 2.13" V4 e-ink driver (SSD1680), landscape mode (250x122).

    Uses MONO_VLSB framebuffer in landscape orientation. Bits are reversed
    per-byte before sending to the SSD1680 which expects MSB-first source data.

    Wiring (directly or via Waveshare Pico e-Paper HAT):
        SPI1 SCK  -> GP10
        SPI1 MOSI -> GP11
        CS        -> GP9
        DC        -> GP8
        RST       -> GP12
        BUSY      -> GP13
    """

    WIDTH = 250
    HEIGHT = 122

    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy

        self.cs.init(Pin.OUT, value=1)
        self.dc.init(Pin.OUT, value=0)
        self.rst.init(Pin.OUT, value=1)
        self.busy.init(Pin.IN)

        pages = (self.HEIGHT + 7) // 8
        self.buffer = bytearray(self.WIDTH * pages)
        self._disp_buf = bytearray(len(self.buffer))
        self.fb = framebuf.FrameBuffer(
            self.buffer, self.WIDTH, self.HEIGHT, framebuf.MONO_VLSB
        )
        self.fb.fill(1)

        self.red_buffer = bytearray(self.WIDTH * pages)
        self._red_disp_buf = bytearray(len(self.red_buffer))
        self.fb_red = framebuf.FrameBuffer(
            self.red_buffer, self.WIDTH, self.HEIGHT, framebuf.MONO_VLSB
        )
        self.fb_red.fill(1)

    def _cmd(self, cmd, data=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([cmd]))
        if data is not None:
            self.dc.value(1)
            self.spi.write(data)
        self.cs.value(1)

    def _wait_busy(self):
        while self.busy.value() == 1:
            time.sleep_ms(10)

    def reset(self):
        self.rst.value(1)
        time.sleep_ms(20)
        self.rst.value(0)
        time.sleep_ms(2)
        self.rst.value(1)
        time.sleep_ms(20)

    def init(self):
        """Initialize display for full refresh in landscape mode."""
        self.reset()
        self._wait_busy()

        self._cmd(0x12)
        self._wait_busy()

        self._cmd(0x01, bytes([249, 0, 0]))
        self._cmd(0x11, bytes([0x07]))
        self._cmd(0x44, bytes([0x00, 0x0F]))
        self._cmd(0x45, bytes([0x00, 0x00, 0xF9, 0x00]))
        self._cmd(0x3C, bytes([0x05]))
        self._cmd(0x21, bytes([0x00, 0x80]))
        self._cmd(0x18, bytes([0x80]))
        self._cmd(0x4E, bytes([0x00]))
        self._cmd(0x4F, bytes([0x00, 0x00]))
        self._wait_busy()

    def _prepare_buf(self):
        for i in range(len(self.buffer)):
            self._disp_buf[i] = _REV[self.buffer[i]]

    def _prepare_red_buf(self):
        for i in range(len(self.red_buffer)):
            self._red_disp_buf[i] = _REV[self.red_buffer[i]]

    def display(self):
        """Full refresh with tri-color (~2-3 s). Clears any ghosting."""
        self._prepare_buf()
        self._prepare_red_buf()
        self._cmd(0x4E, bytes([0x00]))
        self._cmd(0x4F, bytes([0x00, 0x00]))
        self._cmd(0x24, self._disp_buf)
        self._cmd(0x4E, bytes([0x00]))
        self._cmd(0x4F, bytes([0x00, 0x00]))
        self._cmd(0x26, self._red_disp_buf)
        self._cmd(0x22, bytes([0xF7]))
        self._cmd(0x20)
        self._wait_busy()

    def display_partial(self):
        """Partial refresh (~0.3 s). May accumulate ghosting over many updates."""
        self._prepare_buf()
        self._cmd(0x4E, bytes([0x00]))
        self._cmd(0x4F, bytes([0x00, 0x00]))
        self._cmd(0x24, self._disp_buf)
        self._cmd(0x4E, bytes([0x00]))
        self._cmd(0x4F, bytes([0x00, 0x00]))
        self._cmd(0x26, self._disp_buf)
        self._cmd(0x22, bytes([0xFF]))
        self._cmd(0x20)
        self._wait_busy()

    def clear(self):
        """Clear display to white with a full refresh."""
        self.fb.fill(1)
        self.fb_red.fill(1)
        self.display()

    def sleep(self):
        """Enter deep-sleep mode. Call init() to wake."""
        self._cmd(0x10, bytes([0x01]))
