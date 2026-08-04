#!/bin/bash
# Purple Ultra AI - Run Script
# Usage: ./run.sh [command]
# Commands: run, install, test, clean, status

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"
PID_FILE=".purple_ultra.pid"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════╗"
    echo "║       Purple Ultra AI                ║"
    echo "║    Advanced Voice Assistant          ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv "$VENV_DIR"
    fi
    source "$VENV_DIR/bin/activate"
}

install_deps() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}Dependencies installed.${NC}"
}

run_assistant() {
    setup_venv
    source "$VENV_DIR/bin/activate"
    
    echo -e "${GREEN}Starting Purple Ultra AI...${NC}"
    echo "Press Ctrl+C to stop"
    echo ""
    
    python main.py "$@"
}

run_background() {
    setup_venv
    source "$VENV_DIR/bin/activate"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${YELLOW}Already running (PID: $PID)${NC}"
            return
        fi
    fi
    
    echo -e "${GREEN}Starting in background...${NC}"
    nohup python main.py --background > logs/output.log 2>&1 &
    echo $! > "$PID_FILE"
    echo -e "${GREEN}Started (PID: $!)${NC}"
}

stop_assistant() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm -f "$PID_FILE"
            echo -e "${GREEN}Stopped.${NC}"
        else
            rm -f "$PID_FILE"
            echo -e "${YELLOW}Process not running.${NC}"
        fi
    else
        echo -e "${YELLOW}No PID file found.${NC}"
    fi
}

show_status() {
    echo -e "${BLUE}Purple Ultra AI Status${NC}"
    echo "────────────────────"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "Status: ${GREEN}Running${NC} (PID: $PID)"
        else
            echo -e "Status: ${RED}Stopped${NC} (stale PID)"
        fi
    else
        echo -e "Status: ${YELLOW}Not running${NC}"
    fi
    echo ""
    if [ -d "$VENV_DIR" ]; then
        echo "Virtual env: ${GREEN}Ready${NC}"
    else
        echo "Virtual env: ${RED}Not created${NC}"
    fi
    echo ""
    echo "Memory files:"
    ls -la memory/ 2>/dev/null || echo "  (none)"
}

clean_temp() {
    echo -e "${YELLOW}Cleaning temporary files...${NC}"
    rm -rf temp/*
    rm -rf generated/images/*
    echo -e "${GREEN}Cleaned.${NC}"
}

print_banner

case "${1:-run}" in
    run)
        shift
        run_assistant "$@"
        ;;
    voice)
        shift
        run_assistant --voice "$@"
        ;;
    install)
        setup_venv
        install_deps
        ;;
    background|bg)
        run_background
        ;;
    stop)
        stop_assistant
        ;;
    status)
        show_status
        ;;
    clean)
        clean_temp
        ;;
    test)
        setup_venv
        source "$VENV_DIR/bin/activate"
        python -m pytest tests/ -v 2>/dev/null || echo "No tests found"
        ;;
    *)
        echo "Usage: $0 {run|voice|install|background|stop|status|clean|test}"
        echo ""
        echo "Commands:"
        echo "  run         - Run in interactive text mode (default)"
        echo "  voice       - Run in voice-first mode"
        echo "  install     - Install dependencies"
        echo "  background  - Run in background"
        echo "  stop        - Stop background process"
        echo "  status      - Show status"
        echo "  clean       - Clean temporary files"
        echo "  test        - Run tests"
        ;;
esac
