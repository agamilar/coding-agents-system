#!/bin/bash

# Quick Start Script for Coding Agents System
# This script helps you set up and run the system quickly

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_green() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_yellow() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_red() {
    echo -e "${RED}✗ $1${NC}"
}

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup
print_header "Coding Agents System - Quick Start"

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists docker; then
    print_red "Docker is not installed"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi
print_green "Docker found"

if ! command_exists docker-compose; then
    print_red "Docker Compose is not installed"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi
print_green "Docker Compose found"

# Check if .env exists
if [ ! -f .env ]; then
    print_yellow ".env file not found, creating from template..."
    cp .env.example .env
    print_green "Created .env file"
    print_yellow "Please edit .env file and add your credentials:"
    echo "  - GITHUB_APP_ID"
    echo "  - GITHUB_WEBHOOK_SECRET"
    echo "  - LLM API KEY (OpenAI, Anthropic, or Yandex)"
    echo ""
    read -p "Press Enter when you've configured .env..."
fi

# Check if private key exists
if [ ! -d keys ]; then
    mkdir -p keys
    print_green "Created keys directory"
fi

if [ ! -f keys/private-key.pem ]; then
    print_yellow "GitHub App private key not found"
    echo "Please place your private-key.pem file in the keys/ directory"
    echo ""
    read -p "Press Enter when you've added the private key..."
fi

if [ -f keys/private-key.pem ]; then
    chmod 600 keys/private-key.pem
    print_green "Private key permissions set"
fi

# Ask about deployment mode
print_header "Deployment Mode"
echo "Choose deployment mode:"
echo "1) Local with ngrok tunnel (recommended for development)"
echo "2) Local without tunnel (use if you have public IP)"
echo "3) Production (no ngrok)"
echo ""
read -p "Enter choice [1-3]: " deploy_choice

case $deploy_choice in
    1)
        print_green "Using local mode with ngrok tunnel"
        
        # Check if ngrok token is set
        if ! grep -q "NGROK_AUTH_TOKEN=.*[a-zA-Z0-9]" .env; then
            print_yellow "Ngrok auth token not found in .env"
            echo "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
            read -p "Enter ngrok auth token: " ngrok_token
            
            # Update .env
            if grep -q "NGROK_AUTH_TOKEN=" .env; then
                sed -i.bak "s/NGROK_AUTH_TOKEN=.*/NGROK_AUTH_TOKEN=${ngrok_token}/" .env
            else
                echo "NGROK_AUTH_TOKEN=${ngrok_token}" >> .env
            fi
            
            print_green "Ngrok token added to .env"
        fi
        
        # Ensure USE_NGROK is true
        sed -i.bak "s/USE_NGROK=.*/USE_NGROK=true/" .env
        
        COMPOSE_COMMAND="docker-compose --profile ngrok up -d"
        ;;
    2)
        print_green "Using local mode without tunnel"
        sed -i.bak "s/USE_NGROK=.*/USE_NGROK=false/" .env
        COMPOSE_COMMAND="docker-compose up -d"
        ;;
    3)
        print_green "Using production mode"
        sed -i.bak "s/USE_NGROK=.*/USE_NGROK=false/" .env
        COMPOSE_COMMAND="docker-compose up -d"
        ;;
    *)
        print_red "Invalid choice"
        exit 1
        ;;
esac

# Build and start containers
print_header "Starting Coding Agents System"

echo "Building Docker images..."
docker-compose build

echo "Starting containers..."
eval $COMPOSE_COMMAND

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Check if app is running
if docker-compose ps | grep -q "app.*Up"; then
    print_green "Application is running!"
else
    print_red "Application failed to start"
    echo "Check logs with: docker-compose logs app"
    exit 1
fi

# Display access information
print_header "System Ready!"

echo "Application is running on:"
echo "  Local: http://localhost:3000"

if [ "$deploy_choice" = "1" ]; then
    echo ""
    echo "Ngrok tunnel information:"
    echo "  Dashboard: http://localhost:4040"
    echo ""
    print_yellow "Getting ngrok URL..."
    sleep 3
    
    # Try to get ngrok URL
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null || echo "Not available yet")
    
    if [ "$NGROK_URL" != "Not available yet" ]; then
        echo "  Public URL: $NGROK_URL"
        echo "  Webhook URL: $NGROK_URL/webhook"
        echo ""
        print_yellow "Update your GitHub App webhook URL to:"
        echo "  $NGROK_URL/webhook"
    else
        echo ""
        print_yellow "Ngrok URL not ready yet. Check the dashboard at http://localhost:4040"
    fi
fi

echo ""
echo "Health check: http://localhost:3000/health"
echo "Setup info: http://localhost:3000/setup"
echo ""

# Test health endpoint
echo "Testing health endpoint..."
if curl -s http://localhost:3000/health | grep -q "healthy"; then
    print_green "Health check passed!"
else
    print_yellow "Health check pending... Service may still be starting"
fi

echo ""
print_header "Next Steps"
echo "1. Update GitHub App webhook URL (if using ngrok)"
echo "2. Install GitHub App on your repository"
echo "3. Create an Issue to test the system"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop system:  docker-compose down"
echo "  Restart:      docker-compose restart"
echo ""

print_green "Setup complete! Happy coding! 🚀"
