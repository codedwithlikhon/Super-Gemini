#!/bin/bash
# A script to set up the Ubuntu environment for Super-Gemini using proot-distro.

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

echo -e "${YELLOW}🚀 Starting Ubuntu environment setup...${NC}\n"

echo -e "${BLUE}[1/3] Installing proot-distro...${NC}"
pkg install proot-distro -y
echo -e "${GREEN}✓ proot-distro installed${NC}\n"

echo -e "${BLUE}[2/3] Installing Ubuntu...${NC}"
proot-distro install ubuntu
echo -e "${GREEN}✓ Ubuntu installation complete${NC}\n"

echo -e "${BLUE}[3/3] Installing development tools in Ubuntu...${NC}"
proot-distro exec ubuntu -- /bin/bash -c 'apt-get update && apt-get install -y build-essential git python3 python3-pip nodejs npm sqlite3'
echo -e "${GREEN}✓ Development tools installed${NC}\n"

echo -e "${GREEN}✨ Ubuntu environment is ready!${NC}"
echo -e "${CYAN}Super-Gemini is now configured to run in Ubuntu environment.${NC}\n"

# Feature summary
echo -e "${YELLOW}Available features in Ubuntu:${NC}"
echo -e "${GREEN}✓${NC} Full Linux development environment"
echo -e "${GREEN}✓${NC} Build tools and compilers"
echo -e "${GREEN}✓${NC} Python 3 with pip"
echo -e "${GREEN}✓${NC} Node.js and npm"
echo -e "${GREEN}✓${NC} SQLite database"
echo -e "${GREEN}✓${NC} Git version control\n"

echo -e "${BLUE}To enter Ubuntu environment, run:${NC}"
echo -e "${CYAN}proot-distro login ubuntu${NC}"
