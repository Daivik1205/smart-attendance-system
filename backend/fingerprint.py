# fingerprint.py
from pyfingerprint.pyfingerprint import PyFingerprint
import time

class FingerprintSensor:
    def __init__(self):
        self.sensor = self._init_sensor()
        
    def _init_sensor(self):
        try:
            # Use /dev/serial0 for Pi UART pins TX/14, RX/15
            sensor = PyFingerprint('/dev/serial0', 57600, 0xFFFFFFFF, 0x00000000)
            if not sensor.verifyPassword():
                raise ValueError('Invalid sensor password')
            print('Fingerprint sensor initialized')
            return sensor
        except Exception as e:
            print('Sensor init failed:', str(e))
            return None

    def enroll(self):
        if not self.sensor:
            return None

        try:
            # First read
            print("Waiting for finger...")
            while not self.sensor.readImage():
                pass

            self.sensor.convertImage(0x01)

            # Check if finger already exists
            result = self.sensor.searchTemplate()
            if result[0] >= 0:
                print("Finger already exists at position #" + str(result[0]))
                return None

            print("Remove finger")
            time.sleep(2)

            print("Place same finger again")
            while not self.sensor.readImage():
                pass

            self.sensor.convertImage(0x02)

            if self.sensor.compareCharacteristics() == 0:
                print("Fingers do not match")
                return None

            self.sensor.createTemplate()
            position_number = self.sensor.storeTemplate()
            print(f"Fingerprint enrolled at position #{position_number}")
            return position_number

        except Exception as e:
            print("Enrollment failed:", str(e))
            return None

    def verify(self):
        if not self.sensor:
            return None

        try:
            print("Waiting for finger to verify...")
            while not self.sensor.readImage():
                pass

            self.sensor.convertImage(0x01)
            result = self.sensor.searchTemplate()
            
            if result[0] == -1:
                print("No match found")
                return None

            print(f"Match found at position #{result[0]}")
            return result[0]

        except Exception as e:
            print("Verification failed:", str(e))
            return None