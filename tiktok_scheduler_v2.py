
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
from playwright.async_api import Playwright, async_playwright, expect

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
        # Check if already logged in by looking for a specific element
        await page.goto("https://www.tiktok.com/")
        await page.wait_for_load_state("networkidle")
        # Check for elements that are only visible when logged in
        # This might need to be adjusted based on TikTok's UI changes
        return await page.is_visible("div[data-e2e=\"feed-video-card\"]") or \
               await page.is_visible("button[data-e2e=\"upload-btn\"]") or \
               await page.is_visible("a[href=\"/upload\"]")

    async def login(self, page):
        cls(); banner()
        divider("LOGIN — Playwright Automation")
        print()

        username = self.cfg.get("tiktok_username") or prompt("TikTok Username")
        password = self.cfg.get("tiktok_password") or prompt("TikTok Password", hide_input=True) # hide_input not supported by default prompt

        if not username or not password:
            status("TikTok username and password are required.", "err")
            return False

        self.cfg["tiktok_username"] = username
        self.cfg["tiktok_password"] = password # In a real app, this should be encrypted
        save_config(self.cfg)

        status("Navigating to TikTok login page...", "run")
        await page.goto("https://www.tiktok.com/login")
        await page.wait_for_load_state("networkidle")

        # Click 'Use phone / email / username' if present
        if await page.is_visible("text=Use phone / email / username"): # Check if the option is visible
            await page.click("text=Use phone / email / username")
            await page.wait_for_load_state("networkidle")

        # Fill in credentials
        # TikTok uses different selectors for username/email/phone input
        # We'll try to find a common input field or specific ones
        try:
            await page.fill("input[name=\"username\"]", username, timeout=5000)
        except:
            try:
                await page.fill("input[name=\"email\"]", username, timeout=5000)
            except:
                await page.fill("input[name=\"phone\"]", username, timeout=5000)

        await page.fill("input[name=\"password\"]", password)

        # Click the login button
        await page.click("button[type=\"submit\"]")

        status("Waiting for login to complete...", "run")
        try:
            await page.wait_for_url("https://www.tiktok.com/foryou", timeout=30000) # Wait for redirect to For You page
            status("Login successful!", "ok")
            return True
        except Exception as e:
            status(f"Login failed: {e}", "err")
            # Add more robust error checking here, e.g., check for error messages on page
            return False

    def logout(self):
        for key in ("tiktok_username", "tiktok_password"):
            self.cfg.pop(key, None)
        save_config(self.cfg)
        status("Logged out.", "ok")

# ── AI Content Generator ──────────────────────────────
class ContentGenerator:
    """Generates title, description, hashtags using simple heuristics
       (replace with real AI API call if desired)."""

    TAGS = [
        "#fyp", "#foryou", "#viral", "#trending", "#explore",
        "#video", "#content", "#creator", "#tiktok", "#reels",
    ]

    def generate(self, filename):
        base = Path(filename).stem.replace("_", " ").replace("-", " ").title()
        title = base[:90]
        desc  = f"{base} — Watch till the end! 🔥"
        tags  = " ".join(self.TAGS[:7])
        return title, desc, tags

# ── Playwright-based Uploader ──────────────────────────
class TikTokUploaderPlaywright:
    def __init__(self, cfg):
        self.cfg = cfg

    async def upload(self, page, filepath, title, desc, tags):
        status(f"Navigating to upload page for {Path(filepath).name}...", "run")
        await page.goto("https://www.tiktok.com/upload?lang=en") # Use English version for consistent selectors
        await page.wait_for_load_state("networkidle")

        # Check if login is required again
        if not await TikTokAuthPlaywright(self.cfg).is_logged_in(page):
            status("Not logged in, attempting to log in before upload.", "warn")
            if not await TikTokAuthPlaywright(self.cfg).login(page):
                return False, "Failed to log in for upload."
            await page.goto("https://www.tiktok.com/upload?lang=en") # Go back to upload page after login
            await page.wait_for_load_state("networkidle")

        try:
            # Upload video file
            # Wait for the upload input element to be visible
            upload_box = await page.wait_for_selector("div[data-e2e=\"upload-box\"]", timeout=15000)
            file_input = await upload_box.locator("input[type=\"file\"]")
            await file_input.set_input_files(filepath)
            status(f"Uploaded file: {Path(filepath).name}", "info")

            # Wait for processing to complete and caption field to appear
            await page.wait_for_selector("[aria-label=\"Caption\"]", timeout=60000)

            # Fill in caption/description
            caption_text = f"{title}\n{desc}\n{tags}"
            await page.fill("[aria-label=\"Caption\"]", caption_text)
            status("Filled caption.", "info")

            # Set privacy to 'Public' (or other desired setting)
            # This might require clicking a dropdown and selecting an option
            # For now, we'll assume the default is fine or handle it later if needed
            # await page.click("div[aria-label=\"Who can watch this video\"]")
            # await page.click("text=Public")

            # Click the \'Post\' button
            await page.click("button[data-e2e=\"post-button\"]")

            status("Waiting for upload to complete...", "run")
            # Wait for a success indicator or redirection to profile page
            await page.wait_for_url(lambda url: "/video/" in url or "/user/" in url, timeout=120000) # Wait for video URL or user profile
            status("Video uploaded successfully (or redirected to profile)!", "ok")
            return True, "Upload successful via Playwright"

        except Exception as e:
            status(f"Upload failed: {e}", "err")
            return False, str(e)

# ── Queue Manager ─────────────────────────────────────
class UploadQueue:
    def __init__(self, cfg, page):
        self.cfg       = cfg
        self.page      = page
        self.gen       = ContentGenerator()
        self.uploader  = TikTokUploaderPlaywright(cfg)
        self.videos    = []
        self.interval  = 1800   # default 30 min
        self.paused    = False
        self.stopped   = False

    def _pick_folder(self):
        cls(); banner(); divider("SELECT VIDEO FOLDER")
        print()
        folder = prompt("Enter folder path containing videos", os.path.expanduser("~/Videos"))
        folder = os.path.expanduser(folder)
        if not os.path.isdir(folder):
            status(f"Folder not found: {folder}", "err")
            return []
        exts = ["*.mp4","*.mov","*.avi","*.mkv","*.webm"]
        files = []
        for e in exts:
            files.extend(glob.glob(os.path.join(folder, e)))
        files.sort()
        return files

    def _pick_interval(self):
        cls(); banner(); divider("SCHEDULE SETTINGS")
        print(f"""
  {YL}Interval between uploads:{R}

  {BD}[1]{R}  30 minutes
  {BD}[2]{R}  1 hour
  {BD}[3]{R}  2 hours
  {BD}[4]{R}  Custom (seconds)
""")
        ch = prompt("Choice", "1")
        mapping = {"1": 1800, "2": 3600, "3": 7200}
        if ch in mapping:
            return mapping[ch]
        try:
            return int(prompt("Enter interval in seconds", "1800"))
        except ValueError:
            return 1800

    def build_queue(self):
        files = self._pick_folder()
        if not files:
            status("No video files found.", "warn")
            input("  Press Enter to go back...")
            return False

        self.interval = self._pick_interval()

        cls(); banner(); divider("QUEUE PREVIEW")
        print()
        gen = ContentGenerator()
        self.videos = []
        for i, f in enumerate(files[:100], 1):
            title, desc, tags = gen.generate(f)
            self.videos.append({"path": f, "title": title, "desc": desc, "tags": tags, "status": "pending"})
            size_mb = os.path.getsize(f) / 1024 / 1024
            print(f"  {DM}{i:>3}.{R} {GR}{Path(f).name:<40}{R} {YL}{size_mb:>6.1f} MB{R}")

        print()
        mins = self.interval // 60
        status(f"{len(self.videos)} videos • interval: {mins} min • est. finish: {len(self.videos)*mins} min", "info")
        print()
        confirm = prompt("Start uploading? (y/n)", "y")
        return confirm.lower() == "y"

    async def run(self):
        if not self.videos:
            return
        cls(); banner(); divider("UPLOADING")
        print()
        total   = len(self.videos)
        success = 0
        failed  = 0

        for idx, vid in enumerate(self.videos, 1):
            if self.stopped:
                status("Queue stopped by user.", "warn")
                break

            while self.paused:
                await asyncio.sleep(1)

            name = Path(vid["path"]).name
            print()
            divider(f"Video {idx}/{total}")
            status(f"Uploading: {name}", "run")
            status(f"Title: {vid['title'][:60]}...", "info")

            ok, msg = await self.uploader.upload(
                self.page, vid["path"], vid["title"], vid["desc"], vid["tags"]
            )

            if ok:
                vid["status"] = "done"
                success += 1
                status(f"Success — {msg}", "ok")
            else:
                vid["status"] = "failed"
                failed += 1
                status(f"Failed: {msg}", "err")

            # Wait between uploads (skip after last)
            if idx < total and not self.stopped:
                mins = self.interval // 60
                print()
                status(f"Waiting {mins} min before next upload...", "info")
                countdown(self.interval)

        print()
        divider("SUMMARY")
        print(f"""
  {GR}✔  Success : {success}{R}
  {RD}✖  Failed  : {failed}{R}
  {BL}►  Total   : {total}{R}
""")
        input("  Press Enter to return to menu...")

# ── Main Menu ─────────────────────────────────────────
async def main():
    cfg  = load_config()
    playwright_instance = await async_playwright().start()
    browser = await playwright_instance.chromium.launch(headless=False) # Set headless=True for background operation
    context = await browser.new_context()
    page = await context.new_page()

    auth = TikTokAuthPlaywright(cfg)
    queue = None

    while True:
        cls(); banner()

        logged = await auth.is_logged_in(page)
        log_status = f"{GR}● Logged In{R}" if logged \
                     else f"{RD}○ Not Logged In{R}"

        divider("MAIN MENU")
        print(f"""
  {log_status}

  {BD}{CY}[1]{R}  Login / Re-authenticate
  {BD}{CY}[2]{R}  Logout
  {BD}{\'─\' * 40}{R}
  {BD}{GR}[3]{R}  Build Upload Queue
  {BD}{GR}[4]{R}  Start Queue
  {BD}{\'─\' * 40}{R}
  {BD}{YL}[5]{R}  View Queue Status
  {BD}{RD}[Q]{R}  Quit
""")
        divider()
        ch = input(f"  {YL}>{R} Choice: ").strip().lower()

        if ch == "1":
            await auth.login(page)
            input("  Press Enter to continue...")

        elif ch == "2":
            auth.logout()
            input("  Press Enter to continue...")

        elif ch == "3":
            if not await auth.is_logged_in(page):
                status("Please login first.", "warn")
                input("  Press Enter...")
                continue
            queue = UploadQueue(cfg, page)
            ok = queue.build_queue()
            if not ok:
                queue = None

        elif ch == "4":
            if not queue or not queue.videos:
                status("Build a queue first (option 3).", "warn")
                input("  Press Enter...")
                continue
            queue.stopped = False
            queue.paused  = False
            await queue.run()

        elif ch == "5":
            cls(); banner(); divider("QUEUE STATUS")
            print()
            if not queue or not queue.videos:
                status("No queue built yet.", "warn")
            else:
                for i, v in enumerate(queue.videos, 1):
                    col = {"pending": YL, "done": GR, "failed": RD}.get(v["status"], R)
                    print(f"  {DM}{i:>3}.{R} {col}{v[\'status\'] :<8}{R}  {Path(v[\'path\']).name}")
            print()
            input("  Press Enter to continue...")

        elif ch == "q":
            cls()
            print(f"\n  {CY}TikTok Scheduler Engine — Goodbye!{R}\n")
            await context.close()
            await browser.close()
            await playwright_instance.stop()
            sys.exit(0)

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
