#!/bin/bash

# Set these variables
SERVICE_NAME="rfi_scanner"
PYTHON_SCRIPT_PATH="./src/rfi_scanner/pi_ctrl.py"
PYTHON_PATH="pi_ctrl.py"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_FILENAME"
VENV_PATH="$SCRIPT_DIR/venv"
PYTHON_BIN="$VENV_PATH/bin/python3"

# === CREATE VIRTUAL ENVIRONMENT ===
echo "Creating virtual environment at $VENV_PATH..."
python3 -m venv "$VENV_PATH"

# === ACTIVATE AND INSTALL DEPENDENCIES ===
echo "Installing dependencies from pyproject.toml into virtual environment..."
"$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel
"$PYTHON_BIN" -m pip uninstall -y serial python-serial pyserial
"$PYTHON_BIN" -m pip install . --no-cache-dir --no-build-isolation --config-settings=--install-option=--prefix="$HOME/.local"
"$PYTHON_BIN" -m pip install pyserial


WORKING_DIR="$(dirname "$(realpath $PYTHON_SCRIPT_PATH)")"


# Create the systemd service file
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Creating systemd service file at $SERVICE_FILE"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Auto-start Python script: $PYTHON_SCRIPT_PATH
After=network.target

[Service]
ExecStart=$PYTHON_BIN  $PYTHON_PATH
WorkingDirectory=$WORKING_DIR
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