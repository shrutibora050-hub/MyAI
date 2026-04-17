#!/bin/bash
# Verify .env setup for all services

echo "==================================="
echo "Environment Variables Verification"
echo "==================================="
echo ""

check_env_file() {
    local dir=$1
    local service=$2
    
    echo "[$service]"
    if [ -f "$dir/.env" ]; then
        echo "  ✓ .env file exists"
        
        # Check if passwords are still default
        if grep -q "scraper_password\|jobqueue_password" "$dir/.env" 2>/dev/null; then
            echo "  ⚠️  WARNING: Using default passwords! Change them for security."
        else
            echo "  ✓ Custom passwords configured"
        fi
    else
        echo "  ✗ .env file missing! Copy from .env.example"
    fi
    
    if [ -f "$dir/.env.example" ]; then
        echo "  ✓ .env.example exists"
    else
        echo "  ✗ .env.example missing!"
    fi
    echo ""
}

# Check .gitignore
echo "[Root]"
if [ -f ".gitignore" ]; then
    echo "  ✓ .gitignore exists"
    if grep -q "^\.env$" ".gitignore"; then
        echo "  ✓ .env is excluded from git"
    else
        echo "  ✗ .env not in .gitignore!"
    fi
else
    echo "  ✗ .gitignore missing!"
fi
echo ""

# Check each service
check_env_file "Database" "PostgreSQL"
check_env_file "DatabaseManager" "RabbitMQ & DB Manager"
check_env_file "APIGateway" "API Gateway"
check_env_file "Scheduler" "Scheduler"

echo "==================================="
echo "Verification Complete"
echo "==================================="
