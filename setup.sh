#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "[*] Setting up Super-Gemini runtime..."

# Update Termux system
pkg update -y && pkg upgrade -y

# Core tools
pkg install -y git curl wget bash coreutils

# Python + pip
pkg install -y python
pip install --upgrade pip
pip install openai google-genai requests

# Node.js
pkg install -y nodejs

# SQLite
pkg install -y sqlite

# Clone Super-Gemini if missing
if [ ! -d "$HOME/Super-Gemini" ]; then
  git clone https://github.com/codedwithlikhon/Super-Gemini.git ~/Super-Gemini
fi

echo "[*] Super-Gemini setup complete! Ready to launch."
