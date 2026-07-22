"""Utility: paste into the MicroPython REPL to set the DS3231 clock.

Edit the values below, then copy-paste the whole block into the REPL
(or run with: import set_time).
"""
from machine import Pin, I2C
from rtc import DS3231

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
rtc = DS3231(i2c)

YEAR    = 2026
MONTH   = 7
DAY     = 22
WEEKDAY = 3      # 1=Mon ... 7=Sun
HOUR    = 14     # 24-hour format
MINUTE  = 30
SECOND  = 0

rtc.set_datetime(YEAR, MONTH, DAY, WEEKDAY, HOUR, MINUTE, SECOND)
print("RTC set to", rtc.datetime())
