#!/bin/bash

echo "Starting Frontend Server..."

# Navigate to the frontend directory
cd /home/pi/smart_attendance_system/frontend  # Update this path if necessary

# Start the React development server with external access
npm start -- --host 0.0.0.0

echo "Frontend server started successfully"