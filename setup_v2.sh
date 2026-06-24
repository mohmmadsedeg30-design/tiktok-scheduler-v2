#!/usr/bin/env bash
# ═══════════════════════════════════════════════
#   TIKTOK SCHEDULER ENGINE v2.0 — Setup Script (Termux Optimized)
# ═══════════════════════════════════════════════

CY="\033[96m"; GR="\033[92m"; YL="\033[93m"; RD="\033[91m"; R="\033[0m"; BD="\033[1m"

echo -e "\n${CY}${BD}  TIKTOK SCHEDULER ENGINE v2.0 — Setup${R}\n"

# Check if running in Termux
if [ -d "/data/data/com.termux" ]; then
    echo -e "  ${YL}► Termux detected. Installing system dependencies...${R}"
    pkg update -y
    pkg install -y python tur-repo
    pkg install -y playwright-python # Installing playwright via tur-repo if available or explaining manual steps
    
    # Note for Termux users
    echo -e "\n  ${YL}⚠  Note for Termux users:${R}"
    echo -e "  Playwright requires a graphical environment or a specific setup on Termux."
    echo -e "  If 'pip install playwright' fails, try: ${CY}pkg install playwright-python${R}"
fi

# Install Python dependencies
echo -e "  ${GR}► Installing Python dependencies...${R}"
pip install playwright --quiet

# Install Playwright browser binaries
echo -e "  ${GR}► Installing Playwright browser binaries...${R}"
if ! playwright install chromium --with-deps; then
    echo -e "  ${RD}✖  Failed to install playwright browsers automatically.${R}"
    echo -e "  ${YL}Please run 'playwright install chromium' manually if needed.${R}"
fi

echo -e "\n  ${GR}✔  Setup complete!${R}"
echo -e "  ${YL}►  Run with:${R}  python tiktok_scheduler_v2.py\n"
