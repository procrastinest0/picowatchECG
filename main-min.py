from machine import Pin, SPI, I2C
import time
from display import EPD_2in13_V4
from rtc import DS3231
from watchface import draw_watchface

FULL_EVERY = 15

spi = SPI(1, baudrate=4_000_000, polarity=0, phase=0,
          sck=Pin(10), mosi=Pin(11))
epd = EPD_2in13_V4(spi, cs=Pin(9), dc=Pin(8), rst=Pin(12), busy=Pin(13))

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
rtc = DS3231(i2c)

epd.init()

updates = 0
last_min = -1

while True:
    _, _, _, _, hour24, minute, _ = rtc.datetime()

    if minute != last_min:
        h12 = hour24 % 12 or 12
        pm = hour24 >= 12
        if updates % FULL_EVERY == 0:
            epd.init()
            draw_watchface(epd.fb, h12, minute, pm, fb_red=epd.fb_red)
            epd.display()
            epd.init_partial()
        else:
            draw_watchface(epd.fb, h12, minute, pm)
            epd.display_partial()
        updates += 1
        last_min = minute

    time.sleep(1)
