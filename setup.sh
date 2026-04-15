#!/bin/bash

echo "Installing MariaDB and dependencies..."
sudo apt-get update
sudo apt-get install -y mariadb-server libmariadb-dev pkg-config

echo " -- Starting MariaDB -- "
sudo service mariadb start

echo " -- Setting root user -- "
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '';"

echo "Configuring Python environment..."
sudo ln -s /usr/bin/pip3 /usr/bin/pip || true

# --- NEW: Check if .venv already exists before creating ---
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment '.venv' created."
else
    echo "Virtual environment '.venv' already exists. Skipping creation."
fi

.venv/bin/pip install --upgrade pip
.venv/bin/pip install 'django==5.2.11'
.venv/bin/pip install mysqlclient

ACTIVATE_COMMAND="source ${PWD}/.venv/bin/activate"
if ! grep -qF "$ACTIVATE_COMMAND" ~/.bashrc; then
    echo "$ACTIVATE_COMMAND" >> ~/.bashrc
    echo "Auto-activation reflected in ~/.bashrc"
fi

echo "Setup complete!"