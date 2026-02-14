#!/bin/bash

# EnlightBook Phase 0 Verification Script
# This script verifies that Phase 0 setup is complete and working

echo "========================================="
echo "EnlightBook Phase 0 - Setup Verification"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker is running"
else
    echo -e "${RED}✗${NC} Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
echo "Checking Docker Compose..."
if docker-compose version > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker Compose is available"
else
    echo -e "${RED}✗${NC} Docker Compose is not available"
    exit 1
fi

# Check if .env file exists
echo "Checking environment file..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
else
    echo -e "${YELLOW}⚠${NC} .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created from template"
fi

# Check project structure
echo ""
echo "Checking project structure..."

required_dirs=(
    "backend/config/settings"
    "backend/apps/users"
    "backend/apps/core"
    "backend/apps/academic"
    "backend/apps/finance"
    "backend/apps/exams"
    "backend/apps/attendance"
    "backend/apps/communication"
    "frontend/app"
    "frontend/lib"
)

all_dirs_exist=true
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} Directory exists: $dir"
    else
        echo -e "${RED}✗${NC} Directory missing: $dir"
        all_dirs_exist=false
    fi
done

# Check required files
echo ""
echo "Checking required files..."

required_files=(
    "backend/manage.py"
    "backend/config/settings/base.py"
    "backend/requirements/base.txt"
    "backend/Dockerfile"
    "frontend/package.json"
    "frontend/next.config.js"
    "frontend/tsconfig.json"
    "frontend/Dockerfile"
    "docker-compose.yml"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} File exists: $file"
    else
        echo -e "${RED}✗${NC} File missing: $file"
        all_files_exist=false
    fi
done

# Summary
echo ""
echo "========================================="
if [ "$all_dirs_exist" = true ] && [ "$all_files_exist" = true ]; then
    echo -e "${GREEN}Phase 0 setup is complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: docker-compose up --build"
    echo "2. Run: docker-compose exec backend python manage.py migrate"
    echo "3. Run: docker-compose exec backend python manage.py createsuperuser"
    echo "4. Access the applications:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend:  http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/api/docs/"
else
    echo -e "${YELLOW}Phase 0 setup has missing components.${NC}"
    echo "Please review the errors above and recreate the missing files/directories."
fi
echo "========================================="
