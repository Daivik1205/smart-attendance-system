# backend/hardware.py

import RPi.GPIO as GPIO
import time
import board
import busio
from adafruit_character_lcd.character_lcd_i2c import Character_LCD_I2C

# --- GPIO Setup ---
GREEN_LED = 18
RED_LED = 23
BUZZER = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

# --- LCD Setup ---
i2c = busio.I2C(board.SCL, board.SDA)
lcd_columns = 16
lcd_rows = 2
lcd = Character_LCD_I2C(i2c, lcd_columns, lcd_rows)

# --- Hardware Functions ---

def lcd_display(line1="", line2=""):
    lcd.clear()
    # Limit to 16 chars per line to avoid LCD issues
    line1 = line1[:16]
    line2 = line2[:16]
    lcd.message = f"{line1}\n{line2}"
    print(f"LCD: {line1} | {line2}")

def led_blink(pin, times=3, delay=0.3):
    for _ in range(times):
        GPIO.output(pin, True)
        time.sleep(delay)
        GPIO.output(pin, False)
        time.sleep(delay)

def buzzer_beep(times=1):
    for _ in range(times):
        GPIO.output(BUZZER, True)
        time.sleep(0.2)
        GPIO.output(BUZZER, False)
        time.sleep(0.2)

def success():
    GPIO.output(GREEN_LED, True)
    buzzer_beep(2)
    time.sleep(1)
    GPIO.output(GREEN_LED, False)

def error():
    GPIO.output(RED_LED, True)
    buzzer_beep(3)
    time.sleep(1)
    GPIO.output(RED_LED, False)

def cleanup():
    lcd.clear()
    GPIO.cleanup()
