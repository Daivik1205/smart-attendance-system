# GPIO Pin configurations
BUTTON_PIN = 23
RED_LED_PIN = 17
GREEN_LED_PIN = 27
BUZZER_PIN = 22

# LCD Configuration
LCD_ADDRESS = 0x27
LCD_WIDTH = 16
LCD_ROWS = 2

# Fingerprint Sensor (R307S via UART)
FINGERPRINT_UART_PORT = '/dev/serial0'  # GPIO UART
FINGERPRINT_BAUDRATE = 57600

# Firebase
FIREBASE_CRED_PATH = 'serviceAccountKey.json'
FIREBASE_DB_URL = 'https://your-project.firebaseio.com'

# System Settings
MAX_SESSION_HOURS = 8  # Automatic shutdown after 8 hours
DEBOUNCE_DELAY = 0.3   # Button debounce time in seconds