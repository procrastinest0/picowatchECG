# PicoWatch ECG

An ECG-style watchface for the Raspberry Pi Pico, Waveshare 2.13" e-ink display, and DS3231 RTC module. Time is displayed as electrocardiogram traces on a single graph — an upward PQRST spike marks the current hour, a downward spike marks the current minute.

![ECG Watchface Preview](preview.png)
*3:23 PM — upward peak at hour 3, downward peak between minutes 20 and 25 (4x scaled from 250x122)*

## How to read it

- **Hours 1–12** are labeled across the top. The ECG R-peak spikes **upward** toward the current hour. The active hour label is inverted (white on black).
- **Minutes 0–59** are labeled across the bottom (every 5). The ECG R-peak spikes **downward** toward the current minute. The nearest 5-minute label is highlighted.
- Both traces share a common baseline through the center of the display, with an ECG-paper grid behind them.
- **AM/PM** indicator sits at the bottom right.

## Hardware

| Component | Description |
|---|---|
| Raspberry Pi Pico | RP2040, running MicroPython |
| Waveshare 2.13" e-Paper V4 | 250x122, SSD1680 controller, B/W |
| DS3231 RTC module | I2C, battery-backed |

## Wiring

| Signal | Pico Pin |
|---|---|
| E-ink SPI SCK | GP10 |
| E-ink SPI MOSI | GP11 |
| E-ink CS | GP9 |
| E-ink DC | GP8 |
| E-ink RST | GP12 |
| E-ink BUSY | GP13 |
| DS3231 SDA | GP0 |
| DS3231 SCL | GP1 |
| DS3231 VCC | 3V3 |
| DS3231 GND | GND |
| Button | GP15 (to GND) |

## Setup

1. Flash MicroPython onto the Pico ([download](https://micropython.org/download/RPI_PICO/)).

2. Copy the project files to the Pico using Thonny or `mpremote`:
   ```
   mpremote cp display.py rtc.py watchface.py main.py set_time.py :
   ```

3. Set the RTC clock. Edit the date/time values in `set_time.py`, then run it once:
   ```
   mpremote run set_time.py
   ```

4. Reset the Pico. The watchface starts automatically via `main.py`.

## Files

| File | Purpose |
|---|---|
| `main.py` | Entry point — reads RTC, renders watchface, updates display every minute |
| `display.py` | SSD1680 e-ink driver configured for landscape mode (250x122) |
| `rtc.py` | DS3231 I2C driver |
| `watchface.py` | ECG watchface renderer — grid, PQRST traces, labels |
| `set_time.py` | One-time utility to set the DS3231 clock |
| `preview.py` | Desktop preview renderer (requires Pillow, not deployed to Pico) |

## Sweep animation

Press the button (GP15) to trigger a sweep animation — the ECG trace travels from left to right across the display like a real heart monitor, then settles at the correct hour and minute positions.

![Sweep Animation](sweep.gif)

## Display updates

- The display does a **full refresh** on the first update and every 15th update to clear ghosting.
- In between, **partial refresh** is used for faster (~0.3 s) updates.
- The main loop polls the RTC every second and only redraws when the minute changes.

## Desktop preview

Generate a preview image at any time without the hardware:

```
pip install Pillow
python preview.py 14 30    # renders 2:30 PM
```
