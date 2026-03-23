"""
Keep Twitter session alive by visiting x.com periodically.
Add to cron: 0 */6 * * * cd /path/to/MoneyPrinterV2 && source venv/bin/activate && python keep_twitter_alive.py
"""
import json
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT_DIR, "config.json"), "r") as f:
    config = json.load(f)

profile_path = config.get("firefox_profile", "")
if not profile_path or not os.path.isdir(profile_path):
    print("[ERROR] firefox_profile not configured in config.json")
    exit(1)

options = Options()
options.add_argument("--headless")
options.add_argument("-profile")
options.add_argument(profile_path)

service = Service(GeckoDriverManager().install())
browser = webdriver.Firefox(service=service, options=options)

browser.get("https://x.com/home")
time.sleep(5)
url = browser.current_url
browser.quit()

if "login" in url or "auth" in url:
    print(f"[WARN] Twitter session expired! URL: {url}")
else:
    print(f"[OK] Twitter session alive. URL: {url}")
