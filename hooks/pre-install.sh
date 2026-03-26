#!/bin/bash
# Pre-installation hook for equity research skill

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating data directories..."
mkdir -p data/cache
mkdir -p reports

echo "Pre-installation complete!"
