#!/usr/bin/env bash
# ═══════════════════════════════════════════════
#   TIKTOK SCHEDULER ENGINE v2.0 — Setup Script
# ═══════════════════════════════════════════════

CY="\033[96m"; GR="\033[92m"; YL="\033[93m"; RD="\033[91m"; R="\033[0m"; BD="\033[1m"

echo -e "\n${CY}${BD}  TIKTOK SCHEDULER ENGINE v2.0 — Setup${R}\n"

# Install Python dependencies
echo -e "  ${GR}► Installing Python dependencies...${R}"
pip install playwright --quiet

# Install Playwright browser binaries
echo -e "  ${GR}► Installing Playwright browser binaries...${R}"
playwright install --with-deps chromium --quiet

echo -e "\n  ${GR}✔  Setup complete!${R}"
echo -e "  ${YL}►  Run with:${R}  python tiktok_scheduler_v2.py\n"
