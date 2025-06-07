from pyfingerprint.pyfingerprint import PyFingerprint
from hardware import lcd_display, success, error
import time

def init_sensor():
    try:
        # Use /dev/serial0 for Pi UART pins (GPIO14/TX, GPIO15/RX)
        sensor = PyFingerprint('/dev/serial0', 57600, 0xFFFFFFFF, 0x00000000)
        if not sensor.verifyPassword():
            raise ValueError('Invalid sensor password')
        print('Fingerprint sensor initialized on UART /dev/serial0')
        return sensor
    except Exception as e:
        print('Sensor init failed:', str(e))
        return None

def enroll_fingerprint():
    sensor = init_sensor()
    if not sensor:
        return None

    lcd_display("Place finger", "for enrollment")
    while not sensor.readImage():
        pass

    sensor.convertImage(0x01)

    result = sensor.searchTemplate()
    positionNumber = result[0]
    if positionNumber >= 0:
        lcd_display("Finger exists", f"at #{positionNumber}")
        error()
        return None

    lcd_display("Remove finger", "")
    time.sleep(2)

    lcd_display("Place same", "finger again")
    while not sensor.readImage():
        pass
    sensor.convertImage(0x02)

    if sensor.compareCharacteristics() == 0:
        lcd_display("Finger mismatch", "Try again")
        error()
        return None

    sensor.createTemplate()
    positionNumber = sensor.storeTemplate()
    lcd_display("Fingerprint OK", f"ID: {positionNumber}")
    success()
    return positionNumber

def verify_fingerprint():
    sensor = init_sensor()
    if not sensor:
        return None

    lcd_display("Place finger", "to verify")
    while not sensor.readImage():
        pass

    sensor.convertImage(0x01)
    result = sensor.searchTemplate()
    positionNumber = result[0]
    if positionNumber == -1:
        lcd_display("No match", "Try again")
        error()
        return None

    lcd_display("Match found", f"ID: {positionNumber}")
    success()
    return positionNumber
