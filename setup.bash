#!/bin/bash

# Set these variables
SERVICE_NAME="rfi_scanner"
SCRIPT_PATH="./src/rfi_scanner/pi_ctrl.py"


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install dependencies from pyproject.toml using pip
echo "Installing dependencies from pyproject.toml..."
python3 -m pip install --upgrade pip
python3 -m pip install . --no-cache-dir --no-build-isolation --config-settings=--install-option=--prefix="$HOME/.local" --disable-pip-version-check


# Create the systemd service file
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Creating systemd service file at $SERVICE_FILE"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Auto-start Python script: $SCRIPT_PATH
After=network.target

[Service]
ExecStart=/usr/bin/python3 $SCRIPT_PATH
WorkingDirectory=$(dirname $SCRIPT_PATH)
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd to recognize the new service
echo "Reloading systemd..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# Enable the service to run on boot
echo "Enabling service..."
sudo systemctl enable $SERVICE_NAME.service

# Optionally start it immediately
read -p "Do you want to start the service now? (y/n): " START_NOW
if [[ "$START_NOW" == "y" ]]; then
    echo "Starting service..."
    sudo systemctl start $SERVICE_NAME.service
    echo "Service started."
else
    echo "You can start it later with: sudo systemctl start $SERVICE_NAME"
fi
