
#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║         TIKTOK SCHEDULER ENGINE  v2.0               ║
║         Playwright Automation Edition                ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import glob
import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

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
║                    v2.0  •  Playwright Automation       ║
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
    """Visual countdown bar"""
    bar_w = 40
    for remaining in range(seconds, 0, -1):
        filled = int((seconds - remaining) / seconds * bar_w)
        bar = f"{GR}{'█' * filled}{DM}{'░' * (bar_w - filled)}{R}"
        mins, secs = divmod(remaining, 60)
        print(f"\r  {bar} {YL}{mins:02d}:{secs:02d}{R}", end="", flush=True)
        time.sleep(1)
    print(f"\r  {GR}{'█' * bar_w}{R} {GR}Done!{R}          ")

# ── Playwright-based Auth ──────────────────────────────
class TikTokAuthPlaywright:
    def __init__(self, cfg):
        self.cfg = cfg

    async def is_logged_in(self, page):
        try:
            await page.goto("https://www.tiktok.com/", timeout=60000)
            await page.wait_for_load_state("networkidle")
            return await page.is_visible("button[data-e2e=\"upload-btn\"]") or \
                   await page.is_visible("a[href=\"/upload\"]")
        except:
            return False

    async def login(self, page):
        cls(); banner()
        divider("LOGIN — Playwright Automation")
        print()

        username = self.cfg.get("tiktok_username") or prompt("TikTok Username")
        password = self.cfg.get("tiktok_password") or prompt("TikTok Password", hide_input=True)

        if not username or not password:
            status("TikTok username and password are required.", "err")
            return False

        self.cfg["tiktok_username"] = username
        self.cfg["tiktok_password"] = password
        save_config(self.cfg)

        status("Navigating to TikTok login page...", "run")
        await page.goto("https://www.tiktok.com/login")
        
        try:
            if await page.is_visible("text=Use phone / email / username"):
                await page.click("text=Use phone / email / username")
            
            await page.fill("input[name=\"username\"]", username, timeout=5000)
            await page.fill("input[name=\"password\"]", password)
            await page.click("button[type=\"submit\"]")

            status("Waiting for login to complete (Check for Captcha on screen)...", "run")
            await page.wait_for_url("https://www.tiktok.com/foryou", timeout=60000)
            status("Login successful!", "ok")
            return True
        except Exception as e:
            status(f"Login timed out or failed: {e}", "err")
            status("If you see a Captcha, please solve it in the browser.", "warn")
            return False

    def logout(self):
        for key in ("tiktok_username", "tiktok_password"):
            self.cfg.pop(key, None)
        save_config(self.cfg)
        status("Logged out.", "ok")

# ── AI Content Generator ──────────────────────────────
class ContentGenerator:
    TAGS = ["#fyp", "#foryou", "#viral", "#trending", "#explore"]
    def generate(self, filename):
        base = Path(filename).stem.replace("_", " ").replace("-", " ").title()
        title = base[:90]
        desc  = f"{base} — Watch till the end! 🔥"
        tags  = " ".join(self.TAGS)
        return title, desc, tags

# ── Playwright-based Uploader ──────────────────────────
class TikTokUploaderPlaywright:
    def __init__(self, cfg):
        self.cfg = cfg

    async def upload(self, page, filepath, title, desc, tags):
        status(f"Navigating to upload page...", "run")
        await page.goto("https://www.tiktok.com/upload?lang=en")
        
        try:
            upload_box = await page.wait_for_selector("div[data-e2e=\"upload-box\"]", timeout=15000)
            file_input = await upload_box.locator("input[type=\"file\"]")
            await file_input.set_input_files(filepath)
            status("File uploaded to browser.", "info")

            await page.wait_for_selector("[aria-label=\"Caption\"]", timeout=60000)
            caption_text = f"{title}\n{desc}\n{tags}"
            await page.fill("[aria-label=\"Caption\"]", caption_text)
            
            await page.click("button[data-e2e=\"post-button\"]")
            status("Post button clicked. Waiting for confirmation...", "run")
            
            await page.wait_for_url(lambda url: "/video/" in url or "/user/" in url, timeout=120000)
            status("Video uploaded successfully!", "ok")
            return True, "Success"
        except Exception as e:
            status(f"Upload failed: {e}", "err")
            return False, str(e)

# ── Queue Manager ─────────────────────────────────────
class UploadQueue:
    def __init__(self, cfg, page):
        self.cfg, self.page = cfg, page
        self.uploader = TikTokUploaderPlaywright(cfg)
        self.videos, self.interval = [], 1800
        self.stopped = False

    def build_queue(self):
        cls(); banner(); divider("SELECT VIDEO FOLDER")
        folder = prompt("Folder path", os.path.expanduser("~/Videos"))
        if not os.path.isdir(folder): return False
        
        files = []
        for e in ["*.mp4","*.mov","*.avi"]:
            files.extend(glob.glob(os.path.join(folder, e)))
        
        if not files: return False
        
        self.videos = [{"path": f, "status": "pending"} for f in sorted(files)]
        gen = ContentGenerator()
        for v in self.videos:
            v["title"], v["desc"], v["tags"] = gen.generate(v["path"])
            
        return True

    async def run(self):
        total = len(self.videos)
        for idx, vid in enumerate(self.videos, 1):
            if self.stopped: break
            divider(f"Video {idx}/{total}")
            name = Path(vid["path"]).name
            status(f"Uploading: {name}", "run")
            
            ok, msg = await self.uploader.upload(self.page, vid["path"], vid["title"], vid["desc"], vid["tags"])
            vid["status"] = "done" if ok else "failed"
            
            if idx < total:
                status(f"Waiting {self.interval//60} min...", "info")
                countdown(self.interval)

# ── Main ──────────────────────────────────────────────
async def main():
    cfg = load_config()
    pw = await async_playwright().start()
    
    # Termux Compatibility: Check for system chromium
    termux_chromium = "/data/data/com.termux/files/usr/bin/chromium-browser"
    launch_args = {"headless": True, "args": ["--no-sandbox", "--disable-gpu"]}
    
    if os.path.exists(termux_chromium):
        launch_args["executable_path"] = termux_chromium
        status("Termux Chromium detected, using system browser.", "ok")
    
    try:
        browser = await pw.chromium.launch(**launch_args)
    except Exception as e:
        status(f"Failed to launch browser: {e}", "err")
        status("Try: pkg install x11-repo chromium", "warn")
        return

    context = await browser.new_context()
    page = await context.new_page()
    auth, queue = TikTokAuthPlaywright(cfg), None

    while True:
        cls(); banner()
        logged = await auth.is_logged_in(page)
        divider("MAIN MENU")
        print(f"  {'[● Logged In]' if logged else '[○ Not Logged In]'}\n")
        print(f"  {CY}[1]{R} Login  {CY}[2]{R} Logout\n  {GR}[3]{R} Build Queue  {GR}[4]{R} Start\n  {RD}[Q]{R} Quit")
        divider()
        
        ch = input(f"  {YL}>{R} Choice: ").strip().lower()
        if ch == "1": await auth.login(page)
        elif ch == "2": auth.logout()
        elif ch == "3":
            queue = UploadQueue(cfg, page)
            if not queue.build_queue(): status("No videos found.", "warn")
        elif ch == "4":
            if queue: await queue.run()
            else: status("Build queue first.", "warn")
        elif ch == "q": break

    await browser.close()
    await pw.stop()

if __name__ == "__main__":
    asyncio.run(main())
