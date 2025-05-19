#!/bin/bash

# Change to the project directory
cd ~/github/note-api-server || { echo "Directory not found!"; exit 1; }

# Variables
REMOTE_USER="cmercer"
REMOTE_HOST="raspberrypi"
SERVICE_FILE="note-api.service"
PY_FILE="server.py"
REMOTE_SERVICE_PATH="/etc/systemd/system/"
REMOTE_APP_PATH="/home/cmercer/note-api/"

# Copy service file (requires root on remote)
scp "$SERVICE_FILE" "$REMOTE_USER@$REMOTE_HOST:/tmp/"
ssh "$REMOTE_USER@$REMOTE_HOST" "sudo mv /tmp/$SERVICE_FILE $REMOTE_SERVICE_PATH"

# Copy server.py
scp "$PY_FILE" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_APP_PATH"

# Restart the service
ssh "$REMOTE_USER@$REMOTE_HOST" "sudo systemctl daemon-reload && sudo systemctl restart note-api.service && sudo systemctl status note-api.service"

echo "Deployment complete."