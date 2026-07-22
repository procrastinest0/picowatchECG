from machine import Pin, SPI, I2C
import time
from display import EPD_2in13_V4
from rtc import DS3231
from watchface import draw_watchface, draw_watchface_sweep, W

BUTTON_PIN = 15
SWEEP_STEPS = 20

spi = SPI(1, baudrate=4_000_000, polarity=0, phase=0,
          sck=Pin(10), mosi=Pin(11))
epd = EPD_2in13_V4(spi, cs=Pin(9), dc=Pin(8), rst=Pin(12), busy=Pin(13))

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
rtc = DS3231(i2c)

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

epd.init()

FULL_EVERY = 15
updates = 0
last_min = -1


def animate_sweep(h12, minute, is_pm):
    step_w = (W + SWEEP_STEPS - 1) // SWEEP_STEPS
    for step in range(SWEEP_STEPS + 1):
        sweep_x = min(step * step_w, W)
        draw_watchface_sweep(epd.fb, h12, minute, is_pm, sweep_x)
        epd.display_partial()
    draw_watchface(epd.fb, h12, minute, is_pm)
    epd.display()


while True:
    _, _, _, _, hour24, minute, _ = rtc.datetime()
    h12 = hour24 % 12 or 12
    pm = hour24 >= 12

    if minute != last_min:
        draw_watchface(epd.fb, h12, minute, pm)
        if updates % FULL_EVERY == 0:
            epd.display()
        else:
            epd.display_partial()
        updates += 1
        last_min = minute

    if button.value() == 0:
        animate_sweep(h12, minute, pm)
        while button.value() == 0:
            time.sleep_ms(50)

    time.sleep(1)
