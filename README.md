# Smart Attendance System with R307S Fingerprint Sensor

A complete biometric attendance system using Raspberry Pi with:
- R307S fingerprint sensor (connected via GPIO UART)
- Face recognition camera
- LCD display
- Physical buttons and status LEDs
- Firebase realtime database backend
- Web dashboard for monitoring

## Hardware Requirements

- Raspberry Pi 3/4 (recommended)
- R307S Fingerprint Sensor
- Raspberry Pi Camera Module
- 16x2 I2C LCD Display
- Push button
- Red and Green LEDs
- Buzzer
- Jumper wires
- Power supply (2.5A+ recommended)

## Hardware Connections

| R307S Sensor | Raspberry Pi GPIO |
|--------------|------------------|
| VCC          | 5V (Pin 2)       |
| GND          | GND (Pin 6)      |
| TX           | GPIO 14 (Pin 8)  |
| RX           | GPIO 15 (Pin 10) |

Other components:
- LCD: SDA to GPIO 2, SCL to GPIO 3
- Button: GPIO 23
- Red LED: GPIO 17
- Green LED: GPIO 27
- Buzzer: GPIO 22

## Software Installation

1. Install Raspberry Pi OS (Bullseye recommended)

2. Enable required interfaces:
   ```bash
   sudo raspi-config