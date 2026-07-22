class DS3231:
    """DS3231 high-precision RTC over I2C.

    Wiring:
        I2C0 SDA -> GP0
        I2C0 SCL -> GP1
        VCC      -> 3V3
        GND      -> GND
    """

    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr

    @staticmethod
    def _b2d(b):
        return (b >> 4) * 10 + (b & 0x0F)

    @staticmethod
    def _d2b(d):
        return ((d // 10) << 4) | (d % 10)

    def datetime(self):
        """Return (year, month, day, weekday, hour, minute, second).

        Hour is in 24-hour format.
        """
        buf = self.i2c.readfrom_mem(self.addr, 0x00, 7)
        return (
            self._b2d(buf[6]) + 2000,
            self._b2d(buf[5] & 0x1F),
            self._b2d(buf[4] & 0x3F),
            buf[3] & 0x07,
            self._b2d(buf[2] & 0x3F),
            self._b2d(buf[1] & 0x7F),
            self._b2d(buf[0] & 0x7F),
        )

    def set_datetime(self, year, month, day, weekday, hour, minute, second):
        """Set the RTC. Hour must be in 24-hour format."""
        buf = bytearray(7)
        buf[0] = self._d2b(second)
        buf[1] = self._d2b(minute)
        buf[2] = self._d2b(hour)
        buf[3] = weekday
        buf[4] = self._d2b(day)
        buf[5] = self._d2b(month)
        buf[6] = self._d2b(year - 2000)
        self.i2c.writeto_mem(self.addr, 0x00, buf)

    def temperature(self):
        """Read the on-chip temperature sensor (Celsius)."""
        buf = self.i2c.readfrom_mem(self.addr, 0x11, 2)
        t = buf[0]
        if t & 0x80:
            t -= 256
        return t + (buf[1] >> 6) * 0.25
