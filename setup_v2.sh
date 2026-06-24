#!/usr/bin/env bash
# ═══════════════════════════════════════════════
#   TIKTOK SCHEDULER ENGINE v2.0 — Setup (Termux)
# ═══════════════════════════════════════════════

CY="\033[96m"; GR="\033[92m"; YL="\033[93m"; RD="\033[91m"; R="\033[0m"; BD="\033[1m"

echo -e "\n${CY}${BD}  TIKTOK SCHEDULER ENGINE v2.0 — Setup${R}\n"

# 1. Install System Dependencies for Termux
echo -e "  ${GR}► Installing System Dependencies...${R}"
pkg update -y
pkg install -y python x11-repo chromium
pkg install -y tur-repo

# 2. Install Python Packages
echo -e "  ${GR}► Installing Python Packages...${R}"
pip install playwright-core --quiet
pip install playwright --quiet

# 3. Setup Note
echo -e "\n  ${YL}⚠  IMPORTANT FOR TERMUX:${R}"
echo -e "  Playwright cannot download its own browsers on Android."
echo -e "  We have installed ${CY}Chromium${R} via pkg."
echo -e "  The script is now configured to use it automatically.\n"

echo -e "  ${GR}✔  Setup complete!${R}"
echo -e "  ${YL}►  Run with:${R}  python tiktok_scheduler_v2.py\n"
