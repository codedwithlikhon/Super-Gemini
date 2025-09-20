#!/bin/bash
# A script to set up the Ubuntu environment for Super-Gemini using proot-distro.

set -e

echo "🚀 Starting Ubuntu environment setup..."

echo "[1/3] Installing proot-distro..."
pkg install proot-distro -y
echo "✅ proot-distro installed."

echo "[2/3] Installing Ubuntu..."
proot-distro install ubuntu
echo "✅ Ubuntu installation complete."

echo "[3/3] Installing development tools in Ubuntu..."
proot-distro exec ubuntu -- /bin/bash -c 'apt-get update && apt-get install -y build-essential git python3 python3-pip nodejs npm sqlite3'
echo "✅ Development tools installed."

echo "🎉 Ubuntu environment is ready."
