#!/bin/bash

echo "Starting Flask backend..."
cd /home/pi/smart_attendance_project/backend
source venv/bin/activate
python3 api_server.py
