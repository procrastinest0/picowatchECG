from machine import Pin, SPI, I2C, lightsleep, reset
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

_, _, _, _, hour24, minute, _ = rtc.datetime()
h12 = hour24 % 12 or 12
pm = hour24 >= 12

step_w = (W + SWEEP_STEPS - 1) // SWEEP_STEPS
for step in range(SWEEP_STEPS + 1):
    sweep_x = min(step * step_w, W)
    draw_watchface_sweep(epd.fb, h12, minute, pm, sweep_x)
    if step == 0:
        epd.display()
    else:
        epd.display_partial()

draw_watchface(epd.fb, h12, minute, pm, fb_red=epd.fb_red)
epd.display()

while button.value() == 0:
    time.sleep_ms(50)
time.sleep_ms(200)

epd.sleep()
button.irq(trigger=Pin.IRQ_FALLING)
lightsleep()
reset()
