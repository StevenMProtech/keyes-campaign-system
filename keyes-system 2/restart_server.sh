#!/bin/bash
# Restart Flask Server Script

echo "Stopping old Flask processes..."
kill $(ps aux | grep 'python3.11 app.py' | grep -v grep | awk '{print $2}') 2>/dev/null

echo "Waiting for processes to stop..."
sleep 3

echo "Starting Flask server on port 5022..."
cd /home/ubuntu/keyes-system
nohup python3.11 app.py > server.log 2>&1 &

echo "Server restarted! PID: $!"
echo "Check logs with: tail -f /home/ubuntu/keyes-system/server.log"

