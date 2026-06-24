
#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║         TIKTOK SCHEDULER ENGINE  v2.0               ║
║         Selenium Automation Edition (Termux)         ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import glob
from datetime import datetime
from pathlib import Path

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ── Color codes ──────────────────────────────────────
R  = "\033[0m"
BD = "\033[1m"
CY = "\033[96m"
GR = "\033[92m"
YL = "\033[93m"
RD = "\033[91m"
MG = "\033[95m"
BL = "\033[94m"
DM = "\033[2m"

CONFIG_FILE = os.path.expanduser("~/.tiktok_scheduler_config_v2.json")

# ── Helpers ───────────────────────────────────────────
def cls():
    os.system("clear" if os.name != "nt" else "cls")

def banner():
    print(f"""
{CY}{BD}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║    ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗      ║
║       ██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝      ║
║       ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝       ║
║       ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗       ║
║       ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗      ║
║       ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝      ║
║                                                          ║
║          S C H E D U L E R   E N G I N E               ║
║                    v2.0  •  Selenium Automation         ║
╚══════════════════════════════════════════════════════════╝{R}
""")

def divider(title=""):
    w = 58
    if title:
        side = (w - len(title) - 2) // 2
        print(f"{DM}{'─' * side} {BD}{title}{R}{DM} {'─' * side}{R}")
    else:
        print(f"{DM}{'─' * w}{R}")

def status(msg, kind="info"):
    icons = {"info": f"{BL}ℹ", "ok": f"{GR}✔", "warn": f"{YL}⚠", "err": f"{RD}✖", "run": f"{CY}►"}
    icon = icons.get(kind, "•")
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {DM}[{ts}]{R} {icon}  {msg}{R}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def prompt(text, default=None, hide_input=False):
    hint = f" [{default}]" if default else ""
    if hide_input:
        import getpass
        val = getpass.getpass(prompt=f"  {YL}>{R} {text}{hint}: ").strip()
    else:
        val = input(f"  {YL}>{R} {text}{hint}: ").strip()
    return val if val else default

def countdown(seconds):
    bar_w = 40
    for remaining in range(seconds, 0, -1):
        filled = int((seconds - remaining) / seconds * bar_w)
        bar = f"{GR}{'█' * filled}{DM}{'░' * (bar_w - filled)}{R}"
        mins, secs = divmod(remaining, 60)
        print(f"\r  {bar} {YL}{mins:02d}:{secs:02d}{R}", end="", flush=True)
        time.sleep(1)
    print(f"\r  {GR}{'█' * bar_w}{R} {GR}Done!{R}          ")

# ── Browser Engine ─────────────────────────────────────
def get_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    # Termux Specific Path
    termux_bin = "/data/data/com.termux/files/usr/bin/chromium-browser"
    if os.path.exists(termux_bin):
        chrome_options.binary_location = termux_bin
    
    try:
        # On Termux, chromedriver is usually in the path if installed via pkg
        service = Service() 
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        status(f"Browser launch failed: {e}", "err")
        return None

# ── TikTok Automation Logic ────────────────────────────
class TikTokAutomation:
    def __init__(self, driver, cfg):
        self.driver = driver
        self.cfg = cfg
        self.wait = WebDriverWait(self.driver, 20)

    def is_logged_in(self):
        try:
            self.driver.get("https://www.tiktok.com/")
            time.sleep(5)
            # Check for upload button or profile icon
            return len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/upload']")) > 0 or \
                   len(self.driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='profile-icon']")) > 0
        except:
            return False

    def login(self):
        cls(); banner(); divider("LOGIN")
        user = self.cfg.get("tiktok_username") or prompt("Username/Email")
        pwd  = self.cfg.get("tiktok_password") or prompt("Password", hide_input=True)
        
        self.driver.get("https://www.tiktok.com/login/phone-or-email/email")
        time.sleep(3)
        
        try:
            self.driver.find_element(By.NAME, "username").send_keys(user)
            self.driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(pwd)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            status("Waiting for login... Solve Captcha if it appears!", "run")
            time.sleep(15) # Wait for manual captcha/redirect
            
            if "foryou" in self.driver.current_url or self.is_logged_in():
                status("Login Successful!", "ok")
                self.cfg["tiktok_username"], self.cfg["tiktok_password"] = user, pwd
                save_config(self.cfg)
                return True
            else:
                status("Login failed or Captcha required.", "err")
                return False
        except Exception as e:
            status(f"Login Error: {e}", "err")
            return False

    def upload(self, filepath, title, desc, tags):
        status(f"Uploading: {Path(filepath).name}", "run")
        try:
            self.driver.get("https://www.tiktok.com/upload?lang=en")
            time.sleep(5)
            
            # Switch to iframe if necessary (TikTok upload is often in one)
            if len(self.driver.find_elements(By.TAG_NAME, "iframe")) > 0:
                self.driver.switch_to.frame(0)
            
            file_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_input.send_keys(os.path.abspath(filepath))
            
            status("Processing video...", "info")
            time.sleep(10)
            
            caption_box = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Caption']")))
            caption_box.clear()
            caption_box.send_keys(f"{title}\n{desc}\n{tags}")
            
            post_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-e2e='post-button']")))
            post_btn.click()
            
            status("Video Posted!", "ok")
            time.sleep(5)
            return True
        except Exception as e:
            status(f"Upload Error: {e}", "err")
            return False

# ── Main Loop ──────────────────────────────────────────
def main():
    cfg = load_config()
    driver = get_browser()
    if not driver:
        print(f"\n{RD}CRITICAL: Could not start browser. Ensure 'chromium' and 'tur-repo' are installed.{R}")
        return

    bot = TikTokAutomation(driver, cfg)
    
    while True:
        cls(); banner()
        logged = bot.is_logged_in()
        divider("MAIN MENU")
        print(f"  {'[● Logged In]' if logged else '[○ Not Logged In]'}\n")
        print(f"  {CY}[1]{R} Login  {CY}[2]{R} Logout\n  {GR}[3]{R} Start Upload Queue\n  {RD}[Q]{R} Quit")
        divider()
        
        ch = input(f"  {YL}>{R} Choice: ").strip().lower()
        if ch == "1": bot.login()
        elif ch == "2": 
            cfg.clear(); save_config(cfg); status("Logged out.", "ok"); time.sleep(2)
        elif ch == "3":
            if not logged:
                status("Please login first!", "warn"); time.sleep(2); continue
            
            folder = prompt("Folder Path", os.path.expanduser("~/Videos"))
            files = glob.glob(os.path.join(folder, "*.mp4"))
            if not files:
                status("No videos found.", "err"); time.sleep(2); continue
            
            for f in sorted(files):
                bot.upload(f, Path(f).stem, "Automated Upload", "#fyp #viral")
                status("Waiting 30 min...", "info")
                countdown(1800)
        elif ch == "q":
            break

    driver.quit()

if __name__ == "__main__":
    main()
