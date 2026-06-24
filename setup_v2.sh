#!/usr/bin/env bash
# ═══════════════════════════════════════════════
#   TIKTOK SCHEDULER ENGINE v2.0 — Setup (Selenium Termux)
# ═══════════════════════════════════════════════

CY="\033[96m"; GR="\033[92m"; YL="\033[93m"; RD="\033[91m"; R="\033[0m"; BD="\033[1m"

echo -e "\n${CY}${BD}  TIKTOK SCHEDULER ENGINE v2.0 — Setup${R}\n"

# 1. Update and Install System Dependencies
echo -e "  ${GR}► Updating System and Installing Chromium...${R}"
pkg update -y
pkg install -y python x11-repo tur-repo
pkg install -y chromium

# 2. Install Selenium
echo -e "  ${GR}► Installing Selenium Python Library...${R}"
pip install selenium --quiet

# 3. Final Instructions
echo -e "\n  ${GR}✔  Setup complete!${R}"
echo -e "  ${YL}►  Run with:${R}  python tiktok_scheduler_v2.py\n"
echo -e "  ${BD}Note:${R} If you face browser errors, try running: ${CY}pkg install chromium${R} again."
