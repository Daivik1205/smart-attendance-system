import serial
import time
from pyfingerprint.pyfingerprint import PyFingerprint
from config import FINGERPRINT_UART_PORT, FINGERPRINT_BAUDRATE

class FingerprintSensor:
    def __init__(self):
        # Enable UART on Raspberry Pi
        self._enable_uart()
        
        try:
            # Initialize fingerprint sensor via UART
            self.f = PyFingerprint(FINGERPRINT_UART_PORT, FINGERPRINT_BAUDRAT)
            if not self.f.verifyPassword():
                raise ValueError('The given fingerprint sensor password is wrong!')
            print('Fingerprint sensor initialized via GPIO UART')
        except Exception as e:
            print('Fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            raise
            
    def _enable_uart(self):
        """Enable UART on Raspberry Pi GPIO"""
        try:
            # Check if UART is already enabled
            with open('/boot/config.txt', 'r') as f:
                if 'enable_uart=1' not in f.read():
                    # Enable UART
                    with open('/boot/config.txt', 'a') as f:
                        f.write('\nenable_uart=1\n')
                    print("UART enabled in config.txt - reboot required")
                    return False
            return True
        except Exception as e:
            print(f"Error enabling UART: {str(e)}")
            return False
            
    def enroll_finger(self, student_id):
        """Enroll a new fingerprint and return template"""
        print('Waiting for finger...')
        while not self.f.readImage():
            pass
            
        self.f.convertImage(0x01)
        result = self.f.searchTemplate()
        if result[0] >= 0:
            print('Finger already exists at position #' + str(result[0]))
            return None
            
        print('Remove finger...')
        time.sleep(2)
        print('Place same finger again...')
        while not self.f.readImage():
            pass
            
        self.f.convertImage(0x02)
        if self.f.compareCharacteristics() == 0:
            print('Fingers do not match')
            return None
            
        self.f.createTemplate()
        position = self.f.storeTemplate()
        template = self.f.downloadCharacteristics(0x01)
        
        return {
            'position': position,
            'template': template.tolist(),
            'student_id': student_id
        }
        
    def search_finger(self):
        """Search for a fingerprint and return position if found"""
        try:
            print('Waiting for finger...')
            while not self.f.readImage():
                pass
                
            self.f.convertImage(0x01)
            result = self.f.searchTemplate()
            
            if result[0] == -1:
                return None
            else:
                return result[0]
        except Exception as e:
            print('Fingerprint search failed')
            print('Exception: ' + str(e))
            return None