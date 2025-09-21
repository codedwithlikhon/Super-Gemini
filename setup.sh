#!/data/data/com.termux/files/usr/bin/bash
set -e

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ASCII Art with color
echo -e "${CYAN}"
echo '   _____                          _____                _       _ '
echo '  / ____|                        / ____|              (_)     (_)'
echo ' | (___  _   _ _ __   ___ _ __  | |  __  ___ _ __ ___  _ _ __  _ '
echo '  \___ \| | | | '_ \ / _ \ '__| | | |_ |/ _ \ '_ ` _ \| | '_ \| |'
echo '  ____) | |_| | |_) |  __/ |    | |__| |  __/ | | | | | | | | | |'
echo ' |_____/ \__,_| .__/ \___|_|     \_____|\___|_| |_| |_|_|_| |_|_|'
echo '              | |                                                '
echo '              |_|                                                '
echo -e "${NC}"

echo -e "${YELLOW}[*] Setting up Super-Gemini runtime...${NC}\n"

# Update Termux system
echo -e "${BLUE}[1/5] Updating Termux system...${NC}"
pkg update -y && pkg upgrade -y

# Core tools
echo -e "${BLUE}[2/5] Installing core tools...${NC}"
pkg install -y git curl wget bash coreutils
echo -e "${GREEN}✓ Core tools installed${NC}\n"

# Python + pip
echo -e "${BLUE}[3/5] Setting up Python environment...${NC}"
pkg install -y python
pip install --upgrade pip
pip install openai google-genai requests
echo -e "${GREEN}✓ Python environment ready${NC}\n"

# Node.js
echo -e "${BLUE}[4/5] Installing Node.js...${NC}"
pkg install -y nodejs
echo -e "${GREEN}✓ Node.js installed${NC}\n"

# SQLite
echo -e "${BLUE}[5/5] Installing SQLite...${NC}"
pkg install -y sqlite
echo -e "${GREEN}✓ SQLite installed${NC}\n"

# Clone Super-Gemini if missing
if [ ! -d "$HOME/Super-Gemini" ]; then
  echo -e "${PURPLE}Cloning Super-Gemini repository...${NC}"
  git clone https://github.com/codedwithlikhon/Super-Gemini.git ~/Super-Gemini
  echo -e "${GREEN}✓ Repository cloned${NC}\n"
fi

echo -e "${GREEN}✨ Super-Gemini setup complete!${NC}"
echo -e "${CYAN}Ready to launch your AI development journey.${NC}\n"

# Feature summary
echo -e "${YELLOW}Available features:${NC}"
echo -e "${GREEN}✓${NC} Local-first AI agent execution"
echo -e "${GREEN}✓${NC} Multi-runtime support (Bash, Python, Node.js)"
echo -e "${GREEN}✓${NC} Web application scaffolding"
echo -e "${GREEN}✓${NC} Android/Termux integration"
echo -e "${GREEN}✓${NC} Persistent memory management"
echo -e "${GREEN}✓${NC} Comprehensive testing suite\n"

echo -e "${BLUE}To get started, run:${NC}"
echo -e "${CYAN}cd ~/Super-Gemini && python main.py${NC}"
