#!/bin/bash

# Development script for time-server Django project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Time Server Development Script${NC}"
echo "================================"

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry is not installed. Please install Poetry first.${NC}"
    echo "Run: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Function to run commands with poetry
run_poetry() {
    echo -e "${YELLOW}Running: poetry $*${NC}"
    poetry "$@"
}

case "${1:-help}" in
    "install")
        echo -e "${GREEN}Installing dependencies...${NC}"
        run_poetry install
        ;;
    "migrate")
        echo -e "${GREEN}Running migrations...${NC}"
        run_poetry run python manage.py migrate
        ;;
    "runserver")
        echo -e "${GREEN}Starting development server...${NC}"
        run_poetry run python manage.py runserver
        ;;
    "test")
        echo -e "${GREEN}Running tests...${NC}"
        run_poetry run pytest
        ;;
    "lint")
        echo -e "${GREEN}Running linting...${NC}"
        run_poetry run flake8 .
        ;;
    "format")
        echo -e "${GREEN}Formatting code...${NC}"
        run_poetry run black .
        run_poetry run isort .
        ;;
    "shell")
        echo -e "${GREEN}Opening Django shell...${NC}"
        run_poetry run python manage.py shell
        ;;
    "superuser")
        echo -e "${GREEN}Creating superuser...${NC}"
        run_poetry run python manage.py createsuperuser
        ;;
    "help"|*)
        echo "Usage: $0 {install|migrate|runserver|test|lint|format|shell|superuser|help}"
        echo ""
        echo "Commands:"
        echo "  install     Install dependencies"
        echo "  migrate     Run database migrations"
        echo "  runserver   Start development server"
        echo "  test        Run tests"
        echo "  lint        Run linting (flake8)"
        echo "  format      Format code (black + isort)"
        echo "  shell       Open Django shell"
        echo "  superuser   Create Django superuser"
        echo "  help        Show this help message"
        ;;
esac
