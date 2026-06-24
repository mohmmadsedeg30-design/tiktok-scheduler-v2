# TikTok Scheduler Engine v2.0

## Playwright Automation Edition

This project provides a robust TikTok video scheduling and uploading tool using Playwright for browser automation. It bypasses the need for the official TikTok Developer API, offering more flexibility and control over the upload process.

## Features

*   **API-less Upload:** Utilizes Playwright to automate browser interactions for logging in and uploading videos directly to TikTok.
*   **Scheduled Uploads:** Allows scheduling multiple video uploads with customizable intervals.
*   **Content Generation:** Basic heuristic-based title, description, and hashtag generation (can be extended with AI APIs).
*   **Cross-Platform:** Designed to work on Linux environments (e.g., Ubuntu, Termux).
*   **Local Configuration:** Saves login credentials and settings locally for persistent sessions.

## Quick Start

### 1. Setup

Run the setup script to install necessary Python packages and Playwright browser dependencies:

```bash
bash setup_v2.sh
```

### 2. Run the Scheduler

```bash
python tiktok_scheduler_v2.py
```

Follow the on-screen prompts to log in to your TikTok account, build your upload queue, and start scheduling videos.

## Usage

1.  **Login / Re-authenticate:** Use option `[1]` to log in to your TikTok account. You will be prompted for your TikTok username and password. These credentials will be saved locally in `~/.tiktok_scheduler_config_v2.json`.
2.  **Build Upload Queue:** Use option `[3]` to select a folder containing your video files and set the desired upload interval.
3.  **Start Queue:** Use option `[4]` to begin the automated upload process. The script will upload videos one by one with the specified delay.
4.  **View Queue Status:** Use option `[5]` to check the status of your pending, uploaded, and failed videos.

## Important Notes

*   **Browser Automation:** This tool relies on browser automation. Changes to TikTok's website layout or element selectors may break the script. Regular updates might be required.
*   **Security:** Your TikTok username and password are saved locally. Ensure your system is secure. For enhanced security, consider using environment variables or a more robust credential management system.
*   **TikTok Usage Policy:** Be mindful of TikTok's terms of service and usage policies when automating uploads. Excessive or unusual activity might lead to account restrictions.
*   **Video Privacy:** By default, videos are uploaded as `SELF_ONLY` (private). You can modify the `TikTokUploaderPlaywright` class in `tiktok_scheduler_v2.py` to change the privacy level to `PUBLIC_TO_EVERYONE` if desired.

## Troubleshooting

*   If you encounter issues with Playwright, try running `playwright install --with-deps` again.
*   Ensure your video files are in supported formats (`.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`).
*   Check the console output for any error messages during login or upload.

## Contribution

Feel free to fork the repository, submit pull requests, or open issues for bugs and feature requests.
