import RPi.GPIO as GPIO
import time

class LEDBuzzer:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RED_LED_PIN, GPIO.OUT)
        GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        self.off()
        
    def success(self):
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        
    def failure(self):
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        for _ in range(3):
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(0.1)
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        
    def off(self):
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)