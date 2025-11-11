#!/bin/bash
# Quick start script for Wallpaper Manager

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Wallpaper Manager - Quick Start"
echo "================================"
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Run dependency check
echo
echo "Checking dependencies..."
if python3 check_dependencies.py; then
    echo
    echo -e "${GREEN}✓${NC} All dependencies are installed"
else
    echo
    echo -e "${RED}✗${NC} Some dependencies are missing"
    echo
    echo "Would you like to install Python dependencies now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Installing Python dependencies..."
        pip install -r requirements.txt
        echo
        echo "Please install system dependencies manually:"
        echo "  sudo pacman -S python-gobject gtk4 feh"
        echo
        exit 1
    else
        echo "Please install missing dependencies before running."
        exit 1
    fi
fi

# Run startup test
echo
echo "Running startup tests..."
if python3 test_startup.py; then
    echo
    echo -e "${GREEN}✓${NC} All tests passed"
else
    echo
    echo -e "${RED}✗${NC} Some tests failed"
    echo "Please fix the issues above before running."
    exit 1
fi

# Ask user what to run
echo
echo "What would you like to do?"
echo "  1) Start GUI application (Import Popup)"
echo "  2) Start daemon (background service)"
echo "  3) Exit"
echo
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo
        echo "Starting Wallpaper Manager GUI..."
        python3 -m wallpaper_manager
        ;;
    2)
        echo
        echo "Starting Wallpaper Manager Daemon..."
        echo "Press Ctrl+C to stop"
        python3 -m wallpaper_manager.daemon
        ;;
    3)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
