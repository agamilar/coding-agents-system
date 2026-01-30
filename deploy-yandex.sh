#!/bin/bash

# Automatic deployment script for Yandex Cloud
# Run this script on your Yandex Cloud VM

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_green() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_yellow() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_red() {
    echo -e "${RED}✗ $1${NC}"
}

print_blue() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# Check if running on Yandex Cloud
check_yandex_cloud() {
    if curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/ > /dev/null 2>&1; then
        print_green "Running on Yandex Cloud VM"
        return 0
    else
        print_yellow "Not detected as Yandex Cloud VM (this is OK for testing)"
        return 1
    fi
}

print_header "🚀 Coding Agents System - Yandex Cloud Deployment"

echo "This script will:"
echo "  1. Check prerequisites"
echo "  2. Install required packages"
echo "  3. Configure the application"
echo "  4. Set up Nginx reverse proxy"
echo "  5. Configure autostart"
echo "  6. Start the application"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Detect Yandex Cloud
check_yandex_cloud

# Update system
print_header "Updating system packages"
sudo apt update
sudo apt upgrade -y
print_green "System updated"

# Install dependencies
print_header "Installing dependencies"
sudo apt install -y git curl wget nano htop nginx certbot python3-certbot-nginx
print_green "Dependencies installed"

# Check Docker
print_header "Checking Docker installation"
if ! command -v docker &> /dev/null; then
    print_yellow "Docker not found, installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    print_green "Docker installed"
else
    print_green "Docker already installed"
fi

if ! command -v docker-compose &> /dev/null; then
    print_yellow "Docker Compose not found, installing..."
    sudo apt install -y docker-compose
    print_green "Docker Compose installed"
else
    print_green "Docker Compose already installed"
fi

# Add user to docker group
sudo usermod -aG docker $USER
print_green "User added to docker group"

# Get project directory
PROJECT_DIR="$HOME/coding-agents-system"

if [ ! -d "$PROJECT_DIR" ]; then
    print_yellow "Project directory not found at $PROJECT_DIR"
    echo "Please clone the repository first:"
    echo "  git clone <repo-url> $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"
print_green "Project directory found"

# Configure environment
print_header "Configuring environment"

if [ ! -f .env ]; then
    cp .env.example .env
    print_yellow ".env file created, please configure it:"
    echo ""
    echo "Required settings:"
    echo "  - GITHUB_APP_ID"
    echo "  - GITHUB_WEBHOOK_SECRET"
    echo "  - YANDEX_API_KEY"
    echo "  - YANDEX_FOLDER_ID"
    echo ""
    read -p "Press Enter to edit .env file..."
    nano .env
fi

# Check private key
if [ ! -d keys ]; then
    mkdir -p keys
fi

if [ ! -f keys/private-key.pem ]; then
    print_yellow "GitHub App private key not found"
    echo "Please create keys/private-key.pem with your GitHub App private key"
    read -p "Press Enter to create/edit the key file..."
    nano keys/private-key.pem
    chmod 600 keys/private-key.pem
fi

print_green "Configuration completed"

# Get VM IP
print_header "Detecting VM IP address"
VM_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || hostname -I | awk '{print $1}')
print_blue "VM IP: $VM_IP"

# Configure Nginx
print_header "Configuring Nginx"

NGINX_CONFIG="/etc/nginx/sites-available/coding-agents"
sudo tee $NGINX_CONFIG > /dev/null <<EOF
server {
    listen 80;
    server_name $VM_IP;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
sudo ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/coding-agents
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
sudo nginx -t
sudo systemctl restart nginx
print_green "Nginx configured and started"

# Configure systemd service
print_header "Configuring systemd service for autostart"

sudo tee /etc/systemd/system/coding-agents.service > /dev/null <<EOF
[Unit]
Description=Coding Agents System
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=$USER
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable coding-agents
print_green "Systemd service configured"

# Start application
print_header "Starting Coding Agents System"

# Update .env to not use ngrok
sed -i 's/USE_NGROK=.*/USE_NGROK=false/' .env

# Start Docker Compose
docker-compose up -d

print_green "Application started"

# Wait for application to start
echo "Waiting for application to start..."
sleep 10

# Check health
print_header "Checking application health"
if curl -sf http://localhost:3000/health > /dev/null; then
    print_green "Application is healthy!"
    
    echo ""
    echo "Health check response:"
    curl -s http://localhost:3000/health | python3 -m json.tool || curl -s http://localhost:3000/health
else
    print_red "Application health check failed"
    echo "Check logs with: docker-compose logs app"
fi

# Display results
print_header "🎉 Deployment Complete!"

echo "Your Coding Agents System is now running!"
echo ""
echo "Access URLs:"
echo "  Local:    http://localhost:3000"
echo "  Public:   http://$VM_IP"
echo "  Health:   http://$VM_IP/health"
echo "  Webhook:  http://$VM_IP/webhook"
echo ""
echo "GitHub App Configuration:"
echo "  Update your GitHub App Webhook URL to:"
echo "  → http://$VM_IP/webhook"
echo ""
echo "Useful commands:"
echo "  View logs:       docker-compose logs -f"
echo "  Restart:         sudo systemctl restart coding-agents"
echo "  Stop:            sudo systemctl stop coding-agents"
echo "  Check status:    sudo systemctl status coding-agents"
echo "  Update code:     git pull && docker-compose up -d --build"
echo ""

# Optional: SSL setup
echo ""
read -p "Do you have a domain name for SSL setup? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your domain name: " DOMAIN
    
    echo "Setting up SSL with Let's Encrypt..."
    
    # Update Nginx config with domain
    sudo sed -i "s/server_name $VM_IP;/server_name $DOMAIN;/" $NGINX_CONFIG
    sudo nginx -t
    sudo systemctl reload nginx
    
    # Get SSL certificate
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || {
        print_yellow "SSL setup failed. You can run it manually:"
        echo "  sudo certbot --nginx -d $DOMAIN"
    }
    
    print_green "SSL configured for $DOMAIN"
    echo ""
    echo "Update GitHub App Webhook URL to:"
    echo "  → https://$DOMAIN/webhook"
fi

print_header "📊 Next Steps"

echo "1. Update GitHub App webhook URL to: http://$VM_IP/webhook"
echo "2. Install GitHub App on your repository"
echo "3. Create a test Issue"
echo "4. Watch the magic happen!"
echo ""
echo "For monitoring:"
echo "  docker-compose logs -f app"
echo ""
echo "Happy coding! 🚀"
