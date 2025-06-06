#!/bin/bash

# Smart Attendance System Startup Script
# For Raspberry Pi with R307S Fingerprint Sensor via GPIO

echo "Starting Smart Attendance System..."

# Enable UART if not already enabled
if ! grep -q "enable_uart=1" /boot/config.txt; then
    echo "Enabling UART in /boot/config.txt"
    sudo sh -c 'echo "\nenable_uart=1\n" >> /boot/config.txt'
    echo "UART enabled - reboot required"
    exit 1
fi

# Disable serial console if enabled
if [ -f "/etc/systemd/system/serial-getty@ttyS0.service" ]; then
    echo "Disabling serial console"
    sudo systemctl stop serial-getty@ttyS0.service
    sudo systemctl disable serial-getty@ttyS0.service
fi

# Set permissions for serial port
echo "Setting serial port permissions"
sudo chmod a+rw /dev/serial0

# Start the backend server
echo "Starting backend server..."
cd /home/pi/smart_attendance_system/backend
python3 main.py

echo "System started successfully"