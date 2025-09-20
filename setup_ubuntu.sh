#!/bin/bash

# A script to set up the Ubuntu environment for Super-Gemini using proot-distro.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🚀 Starting Ubuntu environment setup for Super-Gemini..."

# 1. Install proot-distro, the tool used to manage Linux distributions in Termux
echo "[1/3] Installing proot-distro..."
pkg install proot-distro -y
echo "✅ proot-distro installed."

# 2. Use proot-distro to install the latest stable version of Ubuntu
echo "[2/3] Installing Ubuntu..."
proot-distro install ubuntu
echo "✅ Ubuntu installation complete."

# 3. Install essential development tools inside the new Ubuntu environment
# We use 'proot-distro exec' to run commands as root within the Ubuntu guest.
# The '--' separates the proot-distro options from the command to be executed.
echo "[3/3] Installing development tools inside Ubuntu (git, python, node, etc.)..."
proot-distro exec ubuntu -- /bin/bash -c ' \
    apt-get update && \
    apt-get install -y build-essential git python3 python3-pip nodejs npm sqlite3 \
'
echo "✅ Development tools installed successfully."

echo "🎉 Ubuntu environment is ready! The agent can now use it with 'proot-distro exec ubuntu ...'"
