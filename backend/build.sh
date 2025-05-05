#!/bin/bash
set -e

echo "Starting build process..."
echo "Python version: $(python --version)"

# Upgrade pip and install basic tools
echo "Upgrading pip and installing basic tools..."
python -m pip install --upgrade pip setuptools wheel

# Install the dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Make scripts executable
echo "Making scripts executable..."
chmod +x prestart.sh

echo "Build completed successfully!" 