#!/usr/bin/env bash
# =============================================================================
# MARR Lab - First-Time Setup Script
# COM617 Industrial Consulting Project - Group 15
# Author: Jose Batalha De Vasconcelos
#
# Run this script once on a fresh machine after cloning the repository.
# It installs all prerequisites, builds required Docker images, installs
# systemd services, and creates the Docker networks.
#
# Usage:
#   cd /path/to/com617-AutomatedNetworkTroubleshooting-1
#   chmod +x setup.sh
#   ./setup.sh
# =============================================================================

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_USER="$(whoami)"
LAB_NAME="MARR Lab"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()    { echo -e "${RED}[FAIL]${NC}  $*"; exit 1; }

echo ""
echo "=============================================="
echo "  $LAB_NAME - First-Time Setup"
echo "  Repo: $REPO_ROOT"
echo "  User: $CURRENT_USER"
echo "=============================================="
echo ""

# -----------------------------------------------------------------------------
# 1. Prerequisite checks
# -----------------------------------------------------------------------------
info "Checking prerequisites..."

command -v docker    >/dev/null 2>&1 || fail "Docker is not installed. Install Docker 24.0+ first."
command -v python3   >/dev/null 2>&1 || fail "Python 3 is not installed."
command -v ansible   >/dev/null 2>&1 || fail "Ansible is not installed. Install ansible-core 2.14+ first."
command -v containerlab >/dev/null 2>&1 || fail "Containerlab is not installed. See https://containerlab.dev/install/"

DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+' | head -1)
info "Docker version: $DOCKER_VERSION"

CLAB_VERSION=$(containerlab version 2>/dev/null | grep "version:" | awk '{print $2}')
info "Containerlab version: $CLAB_VERSION"

ok "Prerequisites present."
echo ""

# -----------------------------------------------------------------------------
# 2. Docker group membership
# -----------------------------------------------------------------------------
info "Checking Docker group membership..."

if ! groups "$CURRENT_USER" | grep -q docker; then
    warn "User $CURRENT_USER is not in the docker group."
    warn "Adding to docker group — you must log out and back in after setup."
    sudo usermod -aG docker "$CURRENT_USER"
fi

ok "Docker group: ok"
echo ""

# -----------------------------------------------------------------------------
# 3. Python dependencies
# -----------------------------------------------------------------------------
info "Installing Python dependencies..."

pip3 install \
    flask \
    requests \
    pysnmp \
    fastavro \
    kafka-python \
    locust \
    hvac \
    python-dotenv \
    netmiko \
    prometheus-client \
    --break-system-packages \
    --quiet

ok "Python dependencies installed."
echo ""

# -----------------------------------------------------------------------------
# 4. Ansible collections
# -----------------------------------------------------------------------------
info "Installing Ansible collections..."

ansible-galaxy collection install community.docker --quiet 2>/dev/null || true

ok "Ansible collections installed."
echo ""

# -----------------------------------------------------------------------------
# 5. Build Docker images
# -----------------------------------------------------------------------------
info "Building marr-frr-snmp:v1 image..."

docker build \
    -f "$REPO_ROOT/containerlab/Dockerfile.frr-snmp" \
    -t marr-frr-snmp:v1 \
    "$REPO_ROOT/containerlab/" \
    --quiet

ok "marr-frr-snmp:v1 built."

info "Building marr-snmp-notifier:v1 image..."

docker build \
    -f "$REPO_ROOT/containerlab/snmp-notifier/Dockerfile" \
    -t marr-snmp-notifier:v1 \
    "$REPO_ROOT/containerlab/snmp-notifier/" \
    --quiet

ok "marr-snmp-notifier:v1 built."
echo ""

# -----------------------------------------------------------------------------
# 6. Docker networks
# -----------------------------------------------------------------------------
info "Creating Docker networks..."

if ! docker network inspect marr-net >/dev/null 2>&1; then
    docker network create --driver bridge --subnet 172.21.0.0/16 marr-net
    ok "marr-net created (172.21.0.0/16)."
else
    ok "marr-net already exists."
fi

echo ""

# -----------------------------------------------------------------------------
# 7. Systemd services — rewrite with correct paths and user
# -----------------------------------------------------------------------------
info "Installing systemd services..."

# marr-receiver
cat > /tmp/marr-receiver.service << EOF
[Unit]
Description=MARR Alert Receiver - COM617 Group 15
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${REPO_ROOT}
EnvironmentFile=${REPO_ROOT}/.env
ExecStart=/usr/bin/python3 ${REPO_ROOT}/python/alert_receiver.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# marr-syslog
cat > /tmp/marr-syslog.service << EOF
[Unit]
Description=MARR Syslog Listener - COM617 Group 15
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${REPO_ROOT}
ExecStart=/usr/bin/python3 ${REPO_ROOT}/python/syslog_listener.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# marr-snmp
cat > /tmp/marr-snmp.service << EOF
[Unit]
Description=MARR SNMP Listener - COM617 Group 15
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/docker exec -i clab-marr-lab-snmp-notifier python3 /opt/snmp_listener.py
ExecStartPre=/bin/sleep 5
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/marr-receiver.service /etc/systemd/system/marr-receiver.service
sudo cp /tmp/marr-syslog.service   /etc/systemd/system/marr-syslog.service
sudo cp /tmp/marr-snmp.service     /etc/systemd/system/marr-snmp.service

sudo systemctl daemon-reload
sudo systemctl enable marr-receiver marr-syslog marr-snmp >/dev/null 2>&1

ok "Systemd services installed and enabled."
echo ""

# -----------------------------------------------------------------------------
# 8. Environment file
# -----------------------------------------------------------------------------
info "Checking .env file..."

if [ ! -f "$REPO_ROOT/.env" ]; then
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    warn ".env created from .env.example."
    warn "You must set MATTERMOST_WEBHOOK_URL in .env before starting the lab."
    warn "Steps:"
    warn "  1. Start the lab once: ansible-playbook scripts/lab-start.yml"
    warn "  2. Open Mattermost at http://localhost:8065"
    warn "  3. Go to: Main Menu > Integrations > Incoming Webhooks > Add"
    warn "  4. Copy the webhook URL into .env: MATTERMOST_WEBHOOK_URL=<url>"
    warn "  5. Restart the receiver: sudo systemctl restart marr-receiver"
else
    ok ".env already exists."
fi

echo ""

# -----------------------------------------------------------------------------
# 9. Reports directory
# -----------------------------------------------------------------------------
info "Ensuring reports directory exists..."
mkdir -p "$REPO_ROOT/reports"
ok "reports/ ready."
echo ""

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo "=============================================="
echo -e "  ${GREEN}Setup complete.${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. If you were added to the docker group, log out and back in."
echo "  2. Set MATTERMOST_WEBHOOK_URL in .env (see instructions above)."
echo "  3. Start the lab:"
echo "       ansible-playbook scripts/lab-start.yml"
echo ""
echo "Access interfaces after startup:"
echo "  OpenNMS   : http://localhost:8980/opennms  (admin / admin)"
echo "  Mattermost: http://localhost:8065"
echo "  Grafana   : http://localhost:3000          (admin / marr2026)"
echo "  Prometheus: http://localhost:9090"
echo "  Vault     : http://localhost:8200"
echo ""
