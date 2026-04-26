#!/bin/bash
# ============================================================
#  Baseline — Health & Fitness Tracker
#  Raspberry Pi Setup Script (Python/Flask)
#  Works on Pi B+ and all other models
#  Usage: bash setup.sh
# ============================================================

set -e
GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Baseline — Setup              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}[1/4] Checking Python...${NC}"
if ! command -v python3 &>/dev/null; then
  sudo apt install python3 python3-pip -y
else
  echo -e "${GREEN}✓ $(python3 --version)${NC}"
fi

echo ""
echo -e "${YELLOW}[2/4] Installing Flask...${NC}"
pip3 install flask --break-system-packages --quiet
echo -e "${GREEN}✓ Flask ready${NC}"

echo ""
echo -e "${YELLOW}[3/4] Creating data directory...${NC}"
mkdir -p data
echo -e "${GREEN}✓ ./data directory ready${NC}"

echo ""
echo -e "${YELLOW}[4/4] Installing systemd service...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH=$(which python3)

sudo tee /etc/systemd/system/baseline.service > /dev/null <<EOF
[Unit]
Description=Baseline Health Tracker
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$PYTHON_PATH server.py
Restart=on-failure
RestartSec=5
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable baseline
sudo systemctl start baseline
echo -e "${GREEN}✓ Baseline service installed and started${NC}"

PI_IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅  Baseline is running!                         ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  Open on any device on your network:              ║${NC}"
echo -e "${GREEN}║  http://$PI_IP:3000                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BLUE}sudo systemctl status baseline${NC}   — check status"
echo -e "  ${BLUE}sudo systemctl restart baseline${NC}  — restart"
echo -e "  ${BLUE}sudo journalctl -u baseline -f${NC}   — live logs"
echo ""
echo -e "  Database: ${YELLOW}$SCRIPT_DIR/data/baseline.json${NC}"
echo ""
