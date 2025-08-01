#!/usr/bin/env python3
"""
Enhanced Magisk Boot Patcher GUI Tool
Author: Based on CircleCashTeam's web implementation
Version: 0.2.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import os
import sys
import zipfile
import shutil
import tempfile
import threading
import platform
import requests
from pathlib import Path
import re
import json
import hashlib
from datetime import datetime
import webbrowser

class MagiskPatcherEnhanced:
    def __init__(self, root):
        self.root = root
        self.root.title("Magisk Boot Patcher v0.2.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set window icon (if available)
        try:
            if platform.system() == "Windows":
                self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Variables
        self.boot_image_path = tk.StringVar()
        self.magisk_apk_path = tk.StringVar()
        self.arch_var = tk.StringVar(value="arm64-v8a")
        
        # Options
        self.keep_verity = tk.BooleanVar(value=True)
        self.keep_force_encrypt = tk.BooleanVar(value=True)
        self.recovery_mode = tk.BooleanVar(value=False)
        self.patch_vbmeta_flag = tk.BooleanVar(value=False)
        self.legacy_sar = tk.BooleanVar(value=False)
        
        # State
        self.temp_dir = None
        self.magiskboot_path = None
        self.boot_image_file = None
        self.magisk_apk_file = None
        self.is_patching = False
        
        # Theme colors
        self.colors = {
            'bg': '#111318',
            'fg': '#e2e2e9',
            'surface': '#1d1f26',
            'surface_variant': '#2c2f36',
            'primary': '#aac7ff',
            'error': '#ffb4ab',
            'success': '#93ff93',
            'warning': '#ffff93',
            'info': '#93c7ff'
        }
        
        self.setup_ui()
        self.check_requirements()
        self.show_welcome_message()
        
    def setup_ui(self):
        # Configure root
        self.root.configure(bg=self.colors['bg'])
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for all widgets
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['primary'])
        style.configure('TButton', background=self.colors['surface_variant'], foreground=self.colors['fg'])
        style.map('TButton',
                 background=[('active', self.colors['primary']), ('pressed', self.colors['surface'])],
                 foreground=[('active', self.colors['bg'])])
        style.configure('TRadiobutton', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TCheckbutton', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('Horizontal.TProgressbar', background=self.colors['primary'])
        
        # Create main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        self.create_header(main_container)
        
        # Create main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        
        # Right panel
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create UI sections
        self.create_file_selection(left_frame)
        self.create_architecture_selection(left_frame)
        self.create_options_section(left_frame)
        self.create_action_buttons(left_frame)
        self.create_terminal_section(right_frame)
        
        # Create status bar
        self.create_status_bar(main_container)
        
    def create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X)
        
        # Title
        title_label = tk.Label(header_frame, 
                              text="🔮 Magisk Boot Patcher",
                              font=('Arial', 20, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['primary'])
        title_label.pack(side=tk.LEFT)
        
        # Version info
        version_label = tk.Label(header_frame,
                                text="v0.2.0",
                                font=('Arial', 10),
                                bg=self.colors['bg'],
                                fg=self.colors['fg'])
        version_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # GitHub button
        github_btn = tk.Button(header_frame,
                              text="GitHub",
                              font=('Arial', 10),
                              bg=self.colors['surface_variant'],
                              fg=self.colors['fg'],
                              bd=0,
                              padx=10,
                              command=lambda: webbrowser.open("https://github.com/topjohnwu/Magisk"))
        github_btn.pack(side=tk.RIGHT)
        
    def create_file_selection(self, parent):
        """Create file selection section"""
        file_frame = ttk.LabelFrame(parent, text="📁 Files", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Boot image selection
        boot_btn = tk.Button(file_frame,
                            text="Select Boot Image",
                            bg=self.colors['surface_variant'],
                            fg=self.colors['fg'],
                            font=('Arial', 10, 'bold'),
                            padx=20,
                            pady=10,
                            command=self.select_boot_image)
        boot_btn.pack(fill=tk.X)
        
        self.boot_label = tk.Label(file_frame,
                                  textvariable=self.boot_image_path,
                                  bg=self.colors['bg'],
                                  fg=self.colors['info'],
                                  font=('Arial', 9),
                                  wraplength=250)
        self.boot_label.pack(fill=tk.X, pady=(5, 10))
        
        # Magisk APK selection
        apk_btn = tk.Button(file_frame,
                           text="Select Magisk APK",
                           bg=self.colors['surface_variant'],
                           fg=self.colors['fg'],
                           font=('Arial', 10, 'bold'),
                           padx=20,
                           pady=10,
                           command=self.select_magisk_apk)
        apk_btn.pack(fill=tk.X)
        
        self.apk_label = tk.Label(file_frame,
                                 textvariable=self.magisk_apk_path,
                                 bg=self.colors['bg'],
                                 fg=self.colors['info'],
                                 font=('Arial', 9),
                                 wraplength=250)
        self.apk_label.pack(fill=tk.X, pady=(5, 0))
        
        # Download latest Magisk button
        download_btn = tk.Button(file_frame,
                                text="↓ Download Latest Magisk",
                                bg=self.colors['surface'],
                                fg=self.colors['primary'],
                                font=('Arial', 9),
                                padx=10,
                                pady=5,
                                command=self.download_latest_magisk)
        download_btn.pack(fill=tk.X, pady=(10, 0))
        
    def create_architecture_selection(self, parent):
        """Create architecture selection section"""
        arch_frame = ttk.LabelFrame(parent, text="🏗️ Architecture", padding=10)
        arch_frame.pack(fill=tk.X, pady=(0, 10))
        
        architectures = [
            ("arm64-v8a (64-bit ARM)", "arm64-v8a"),
            ("armeabi-v7a (32-bit ARM)", "armeabi-v7a"),
            ("x86_64 (64-bit Intel)", "x86_64"),
            ("x86 (32-bit Intel)", "x86")
        ]
        
        for text, value in architectures:
            rb = tk.Radiobutton(arch_frame,
                               text=text,
                               value=value,
                               variable=self.arch_var,
                               bg=self.colors['bg'],
                               fg=self.colors['fg'],
                               selectcolor=self.colors['surface'],
                               activebackground=self.colors['bg'],
                               font=('Arial', 9))
            rb.pack(anchor=tk.W, pady=2)
            
    def create_options_section(self, parent):
        """Create options section"""
        options_frame = ttk.LabelFrame(parent, text="⚙️ Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        options = [
            ("Keep AVB 2.0/dm-verity", self.keep_verity, 
             "Preserves Android Verified Boot"),
            ("Keep force encryption", self.keep_force_encrypt,
             "Preserves forced encryption"),
            ("Recovery Mode", self.recovery_mode,
             "For recovery installation"),
            ("Patch vbmeta flag", self.patch_vbmeta_flag,
             "Patches vbmeta flags"),
            ("Legacy SAR device", self.legacy_sar,
             "For old System-as-Root devices")
        ]
        
        for text, var, tooltip in options:
            cb = tk.Checkbutton(options_frame,
                               text=text,
                               variable=var,
                               bg=self.colors['bg'],
                               fg=self.colors['fg'],
                               selectcolor=self.colors['surface'],
                               activebackground=self.colors['bg'],
                               font=('Arial', 9))
            cb.pack(anchor=tk.W, pady=2)
            
            # Add tooltip
            self.create_tooltip(cb, tooltip)
            
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Patch button
        self.patch_button = tk.Button(button_frame,
                                     text="🚀 PATCH",
                                     bg=self.colors['primary'],
                                     fg=self.colors['bg'],
                                     font=('Arial', 12, 'bold'),
                                     padx=30,
                                     pady=15,
                                     command=self.patch_boot_image)
        self.patch_button.pack(fill=tk.X)
        
        # Clean temp files button
        clean_btn = tk.Button(button_frame,
                             text="🧹 Clean Temp Files",
                             bg=self.colors['surface'],
                             fg=self.colors['fg'],
                             font=('Arial', 9),
                             padx=10,
                             pady=5,
                             command=self.clean_temp_files)
        clean_btn.pack(fill=tk.X, pady=(5, 0))
        
    def create_terminal_section(self, parent):
        """Create terminal output section"""
        terminal_frame = ttk.LabelFrame(parent, text="📜 Output Log", padding=5)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Terminal with custom colors
        self.terminal = scrolledtext.ScrolledText(terminal_frame,
                                                 bg=self.colors['surface'],
                                                 fg=self.colors['fg'],
                                                 font=('Consolas', 10),
                                                 wrap=tk.WORD,
                                                 height=20)
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colors
        self.terminal.tag_config("INFO", foreground=self.colors['info'])
        self.terminal.tag_config("SUCCESS", foreground=self.colors['success'])
        self.terminal.tag_config("ERROR", foreground=self.colors['error'])
        self.terminal.tag_config("WARNING", foreground=self.colors['warning'])
        self.terminal.tag_config("DEBUG", foreground="#888888")
        
        # Control buttons
        control_frame = ttk.Frame(terminal_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        clear_btn = tk.Button(control_frame,
                             text="Clear",
                             bg=self.colors['surface_variant'],
                             fg=self.colors['fg'],
                             font=('Arial', 9),
                             padx=10,
                             command=self.clear_terminal)
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        save_log_btn = tk.Button(control_frame,
                                text="Save Log",
                                bg=self.colors['surface_variant'],
                                fg=self.colors['fg'],
                                font=('Arial', 9),
                                padx=10,
                                command=self.save_log)
        save_log_btn.pack(side=tk.LEFT)
        
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # Status label
        self.status_label = tk.Label(status_frame,
                                    text="Ready",
                                    bg=self.colors['bg'],
                                    fg=self.colors['fg'],
                                    font=('Arial', 9),
                                    anchor=tk.W)
        self.status_label.pack(fill=tk.X)
        
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip,
                            text=text,
                            bg=self.colors['surface_variant'],
                            fg=self.colors['fg'],
                            font=('Arial', 9),
                            padx=5,
                            pady=2)
            label.pack()
            
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def log(self, message, level="INFO"):
        """Log message to terminal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, f"[{timestamp}] ", ("timestamp",))
        self.terminal.insert(tk.END, f"[{level}] ", (level,))
        self.terminal.insert(tk.END, f"{message}\n")
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)
        self.root.update()
        
    def set_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update()
        
    def clear_terminal(self):
        """Clear terminal output"""
        self.terminal.config(state=tk.NORMAL)
        self.terminal.delete(1.0, tk.END)
        self.terminal.config(state=tk.DISABLED)
        
    def save_log(self):
        """Save terminal log to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"magisk_patch_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            content = self.terminal.get(1.0, tk.END)
            with open(filename, 'w') as f:
                f.write(content)
            self.log(f"Log saved to: {filename}", "SUCCESS")
            
    def show_welcome_message(self):
        """Show welcome message"""
        self.log("=" * 60)
        self.log("Magisk Boot Patcher v0.2.0", "INFO")
        self.log("Based on CircleCashTeam's implementation", "INFO")
        self.log("=" * 60)
        self.log("")
        self.log("Instructions:", "INFO")
        self.log("1. Select your boot.img file", "INFO")
        self.log("2. Select Magisk APK or download latest", "INFO")
        self.log("3. Choose your device architecture", "INFO")
        self.log("4. Configure options if needed", "INFO")
        self.log("5. Click PATCH to start", "INFO")
        self.log("")
        
    def check_requirements(self):
        """Check if magiskboot is available"""
        self.set_status("Checking requirements...")
        self.log("Checking for magiskboot...", "INFO")
        
        if platform.system() == "Windows":
            magiskboot_name = "magiskboot.exe"
        else:
            magiskboot_name = "magiskboot"
            
        # Check in current directory
        if os.path.exists(magiskboot_name):
            self.magiskboot_path = os.path.abspath(magiskboot_name)
            self.log(f"Found magiskboot at: {self.magiskboot_path}", "SUCCESS")
            self.set_status("Ready")
        else:
            self.log("magiskboot not found!", "WARNING")
            self.set_status("magiskboot not found")
            self.download_magiskboot_prompt()
            
    def download_magiskboot_prompt(self):
        """Prompt to download magiskboot"""
        result = messagebox.askyesno(
            "Download magiskboot",
            "magiskboot is required but not found.\n\n"
            "Would you like to download it automatically?"
        )
        
        if result:
            # Run download script if available
            if os.path.exists("download_magiskboot.py"):
                self.log("Running download_magiskboot.py...", "INFO")
                threading.Thread(target=self.run_download_script).start()
            else:
                self.log("Please download magiskboot manually from Magisk releases", "WARNING")
                webbrowser.open("https://github.com/topjohnwu/Magisk/releases")
                
    def run_download_script(self):
        """Run magiskboot download script"""
        try:
            result = subprocess.run([sys.executable, "download_magiskboot.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Successfully downloaded magiskboot!", "SUCCESS")
                self.check_requirements()
            else:
                self.log("Failed to download magiskboot", "ERROR")
                self.log(result.stderr, "ERROR")
        except Exception as e:
            self.log(f"Error running download script: {str(e)}", "ERROR")
            
    def download_latest_magisk(self):
        """Download latest Magisk APK"""
        self.log("Fetching latest Magisk release...", "INFO")
        self.set_status("Downloading Magisk...")
        
        thread = threading.Thread(target=self._download_magisk_worker)
        thread.daemon = True
        thread.start()
        
    def _download_magisk_worker(self):
        """Worker thread for downloading Magisk"""
        try:
            # Get latest release info
            api_url = "https://api.github.com/repos/topjohnwu/Magisk/releases/latest"
            response = requests.get(api_url)
            response.raise_for_status()
            
            release_info = response.json()
            version = release_info['tag_name']
            
            # Find APK URL
            apk_url = None
            apk_name = None
            for asset in release_info['assets']:
                if asset['name'].startswith('Magisk') and asset['name'].endswith('.apk'):
                    apk_url = asset['browser_download_url']
                    apk_name = asset['name']
                    break
                    
            if not apk_url:
                self.log("Could not find Magisk APK in latest release", "ERROR")
                return
                
            self.log(f"Found Magisk {version}: {apk_name}", "SUCCESS")
            
            # Download APK
            self.progress.config(mode='determinate')
            self.progress.start()
            
            response = requests.get(apk_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            filename = os.path.join(os.getcwd(), apk_name)
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.progress['value'] = progress
                            self.set_status(f"Downloading: {progress:.1f}%")
                            
            self.progress.stop()
            self.progress.config(mode='indeterminate')
            
            self.log(f"Downloaded to: {filename}", "SUCCESS")
            self.set_status("Download complete")
            
            # Automatically select the downloaded APK
            self.magisk_apk_file = filename
            self.magisk_apk_path.set(apk_name)
            
        except Exception as e:
            self.log(f"Error downloading Magisk: {str(e)}", "ERROR")
            self.progress.stop()
            self.set_status("Download failed")
            
    def select_boot_image(self):
        """Select boot image file"""
        filename = filedialog.askopenfilename(
            title="Select Boot Image",
            filetypes=[
                ("Boot Images", "*.img"),
                ("Binary files", "*.bin"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.boot_image_file = filename
            self.boot_image_path.set(os.path.basename(filename))
            self.log(f"Selected boot image: {os.path.basename(filename)}", "SUCCESS")
            
            # Show file info
            size = os.path.getsize(filename) / (1024 * 1024)
            self.log(f"File size: {size:.2f} MB", "INFO")
            
    def select_magisk_apk(self):
        """Select Magisk APK file"""
        filename = filedialog.askopenfilename(
            title="Select Magisk APK",
            filetypes=[
                ("APK Files", "*.apk"),
                ("ZIP Files", "*.zip"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.magisk_apk_file = filename
            self.magisk_apk_path.set(os.path.basename(filename))
            self.log(f"Selected Magisk APK: {os.path.basename(filename)}", "SUCCESS")
            
            # Try to get version info
            try:
                with zipfile.ZipFile(filename, 'r') as apk:
                    if 'assets/util_functions.sh' in apk.namelist():
                        with apk.open('assets/util_functions.sh') as f:
                            content = f.read().decode('utf-8')
                            match = re.search(r'MAGISK_VER="([^"]+)"', content)
                            if match:
                                version = match.group(1)
                                self.log(f"Magisk version: {version}", "INFO")
            except:
                pass
                
    def clean_temp_files(self):
        """Clean temporary files"""
        self.log("Cleaning temporary files...", "INFO")
        
        temp_dirs = []
        temp_dir_base = tempfile.gettempdir()
        
        # Find Magisk patch temp directories
        for item in os.listdir(temp_dir_base):
            if item.startswith("magisk_patch_"):
                temp_dirs.append(os.path.join(temp_dir_base, item))
                
        if not temp_dirs:
            self.log("No temporary files found", "INFO")
            return
            
        count = 0
        for temp_dir in temp_dirs:
            try:
                shutil.rmtree(temp_dir)
                count += 1
                self.log(f"Removed: {temp_dir}", "SUCCESS")
            except Exception as e:
                self.log(f"Failed to remove {temp_dir}: {str(e)}", "WARNING")
                
        self.log(f"Cleaned {count} temporary directories", "SUCCESS")
        
    def patch_boot_image(self):
        """Start patching process"""
        if self.is_patching:
            self.log("Patching already in progress!", "WARNING")
            return
            
        if not self.boot_image_file:
            messagebox.showerror("Error", "Please select a boot image first!")
            return
            
        if not self.magisk_apk_file:
            messagebox.showerror("Error", "Please select a Magisk APK first!")
            return
            
        if not self.magiskboot_path:
            messagebox.showerror("Error", "magiskboot not found!")
            return
            
        # Confirm action
        result = messagebox.askyesno(
            "Confirm Patch",
            f"Boot image: {os.path.basename(self.boot_image_file)}\n"
            f"Magisk APK: {os.path.basename(self.magisk_apk_file)}\n"
            f"Architecture: {self.arch_var.get()}\n\n"
            "Continue with patching?"
        )
        
        if not result:
            return
            
        # Start patching in thread
        self.is_patching = True
        thread = threading.Thread(target=self._patch_worker)
        thread.daemon = True
        thread.start()
        
    def _patch_worker(self):
        """Worker thread for patching"""
        self.progress.start()
        self.patch_button.config(state=tk.DISABLED, text="⏳ PATCHING...")
        self.set_status("Patching in progress...")
        
        try:
            # Clear terminal
            self.clear_terminal()
            self.log("=" * 60)
            self.log("Starting patch process...", "INFO")
            self.log("=" * 60)
            
            # Create temp directory
            self.temp_dir = tempfile.mkdtemp(prefix="magisk_patch_")
            self.log(f"Working directory: {self.temp_dir}", "INFO")
            
            # Copy boot image
            boot_path = os.path.join(self.temp_dir, "boot.img")
            shutil.copy2(self.boot_image_file, boot_path)
            self.log("Copied boot image to working directory", "SUCCESS")
            
            # Calculate SHA256 of original boot image
            sha256 = self.calculate_sha256(self.boot_image_file)
            self.log(f"Original boot SHA256: {sha256}", "INFO")
            
            # Extract files from APK
            arch = self.arch_var.get()
            self.log(f"Extracting files for architecture: {arch}", "INFO")
            
            needed_files = self.extract_from_apk(self.magisk_apk_file, arch, self.temp_dir)
            
            if not needed_files:
                raise Exception("Failed to extract necessary files from APK")
                
            # Set environment variables
            env = os.environ.copy()
            env['KEEPVERITY'] = 'true' if self.keep_verity.get() else 'false'
            env['KEEPFORCEENCRYPT'] = 'true' if self.keep_force_encrypt.get() else 'false'
            env['RECOVERYMODE'] = 'true' if self.recovery_mode.get() else 'false'
            env['PATCHVBMETAFLAG'] = 'true' if self.patch_vbmeta_flag.get() else 'false'
            env['LEGACYSAR'] = 'true' if self.legacy_sar.get() else 'false'
            
            self.log("Configuration:", "INFO")
            for key in ['KEEPVERITY', 'KEEPFORCEENCRYPT', 'RECOVERYMODE', 'PATCHVBMETAFLAG', 'LEGACYSAR']:
                self.log(f"  {key}: {env[key]}", "INFO")
            
            # Unpack boot image
            self.log("", "")
            self.log("Unpacking boot image...", "INFO")
            result = self.run_command([self.magiskboot_path, "unpack", "boot.img"], 
                                    cwd=self.temp_dir)
            
            if result != 0:
                raise Exception("Failed to unpack boot image!")
                
            # Check ramdisk status
            ramdisk_path = os.path.join(self.temp_dir, "ramdisk.cpio")
            if os.path.exists(ramdisk_path):
                self.log("Checking ramdisk status...", "INFO")
                result = self.run_command([self.magiskboot_path, "cpio", "ramdisk.cpio", "test"], 
                                        cwd=self.temp_dir)
                
                if result == 0:
                    self.log("Stock boot image detected", "SUCCESS")
                    shutil.copy2(ramdisk_path, ramdisk_path + ".orig")
                elif result == 1:
                    self.log("Magisk patched boot image detected", "WARNING")
                    self.run_command([self.magiskboot_path, "cpio", "ramdisk.cpio", 
                                    "extract .backup/.magisk config.orig", "restore"], 
                                   cwd=self.temp_dir)
                    shutil.copy2(ramdisk_path, ramdisk_path + ".orig")
                else:
                    raise Exception("Boot image patched by unsupported programs!")
            else:
                self.log("No ramdisk found (skip_initramfs)", "WARNING")
            
            # Get SHA1 from magiskboot
            self.log("Getting boot image SHA1...", "INFO")
            sha1_output = self.run_command_output([self.magiskboot_path, "sha1", "boot.img"], 
                                                cwd=self.temp_dir)
            sha1 = sha1_output.strip() if sha1_output else ""
            
            if sha1:
                self.log(f"Boot image SHA1: {sha1}", "INFO")
            
            # Compress files
            self.log("", "")
            self.log("Compressing files...", "INFO")
            
            for filename in ["magisk", "magisk32", "magisk64", "init-ld"]:
                if filename in needed_files:
                    src_path = needed_files[filename]
                    xz_path = os.path.join(self.temp_dir, f"{filename}.xz")
                    self.log(f"Compressing {filename}...", "INFO")
                    self.run_command([self.magiskboot_path, "compress=xz", src_path, xz_path])
                    
            # Compress stub.apk
            if "stub.apk" in needed_files:
                src_path = needed_files["stub.apk"]
                xz_path = os.path.join(self.temp_dir, "stub.xz")
                self.log("Compressing stub.apk...", "INFO")
                self.run_command([self.magiskboot_path, "compress=xz", src_path, xz_path])
            
            # Create magiskinit
            if "magiskinit" in needed_files:
                shutil.copy2(needed_files["magiskinit"], 
                           os.path.join(self.temp_dir, "magiskinit"))
            
            # Create config
            config_path = os.path.join(self.temp_dir, "config")
            with open(config_path, 'w') as f:
                f.write(f"KEEPVERITY={env['KEEPVERITY']}\n")
                f.write(f"KEEPFORCEENCRYPT={env['KEEPFORCEENCRYPT']}\n")
                f.write(f"RECOVERYMODE={env['RECOVERYMODE']}\n")
                f.write(f"PATCHVBMETAFLAG={env['PATCHVBMETAFLAG']}\n")
                f.write(f"LEGACYSAR={env['LEGACYSAR']}\n")
                if sha1:
                    f.write(f"SHA1={sha1}\n")
            
            # Patch ramdisk
            if os.path.exists(ramdisk_path):
                self.log("", "")
                self.log("Patching ramdisk...", "INFO")
                
                # Build cpio commands
                cpio_commands = [
                    self.magiskboot_path, "cpio", "ramdisk.cpio",
                    "add 0750 init magiskinit",
                    "mkdir 0750 overlay.d",
                    "mkdir 0750 overlay.d/sbin"
                ]
                
                # Add compressed files
                for filename in ["magisk", "magisk32", "magisk64", "init-ld"]:
                    xz_file = f"{filename}.xz"
                    xz_path = os.path.join(self.temp_dir, xz_file)
                    if os.path.exists(xz_path):
                        cpio_commands.append(f"add 0644 overlay.d/sbin/{xz_file} {xz_file}")
                        
                # Add stub.xz
                stub_xz = os.path.join(self.temp_dir, "stub.xz")
                if os.path.exists(stub_xz):
                    cpio_commands.append("add 0644 overlay.d/sbin/stub.xz stub.xz")
                
                # Add remaining commands
                cpio_commands.extend([
                    "patch",
                    "backup ramdisk.cpio.orig",
                    "mkdir 000 .backup",
                    "add 000 .backup/.magisk config"
                ])
                
                result = self.run_command(cpio_commands, cwd=self.temp_dir)
                
                if result != 0:
                    raise Exception("Failed to patch ramdisk!")
            
            # Patch kernel if needed
            kernel_path = os.path.join(self.temp_dir, "kernel")
            if os.path.exists(kernel_path):
                self.log("", "")
                self.log("Patching kernel...", "INFO")
                
                kernel_patched = False
                
                # Apply kernel patches
                patches = [
                    ("49010054011440B93FA00F71E9000054010840B93FA00F7189000054001840B91FA00F7188010054",
                     "A1020054011440B93FA00F7140020054010840B93FA00F71E0010054001840B91FA00F7181010054"),
                    ("821B8012", "E2FF8F12"),
                    ("70726F63615F636F6E66696700", "70726F63615F6D616769736B00")
                ]
                
                for old_hex, new_hex in patches:
                    result = self.run_command([self.magiskboot_path, "hexpatch", "kernel", 
                                             old_hex, new_hex], cwd=self.temp_dir)
                    if result == 0:
                        kernel_patched = True
                        self.log(f"Applied kernel patch: {old_hex[:16]}...", "SUCCESS")
                
                # Legacy SAR patch
                if env['LEGACYSAR'] == 'true':
                    result = self.run_command([self.magiskboot_path, "hexpatch", "kernel",
                                             "736B69705F696E697472616D667300",
                                             "77616E745F696E697472616D667300"], 
                                            cwd=self.temp_dir)
                    if result == 0:
                        kernel_patched = True
                        self.log("Applied legacy SAR patch", "SUCCESS")
                
                if not kernel_patched:
                    os.remove(kernel_path)
                    self.log("No kernel patches applied", "INFO")
            
            # Patch dtb if exists
            for dt in ["dtb", "kernel_dtb", "extra"]:
                dt_path = os.path.join(self.temp_dir, dt)
                if os.path.exists(dt_path):
                    self.log(f"", "")
                    self.log(f"Checking {dt}...", "INFO")
                    
                    # Test dtb
                    result = self.run_command([self.magiskboot_path, "dtb", dt, "test"], 
                                            cwd=self.temp_dir)
                    if result != 0:
                        self.log(f"{dt} was patched by old Magisk", "WARNING")
                    
                    # Patch dtb
                    result = self.run_command([self.magiskboot_path, "dtb", dt, "patch"], 
                                            cwd=self.temp_dir)
                    if result == 0:
                        self.log(f"Patched {dt} successfully", "SUCCESS")
            
            # Repack boot image
            self.log("", "")
            self.log("Repacking boot image...", "INFO")
            result = self.run_command([self.magiskboot_path, "repack", "boot.img"], 
                                    cwd=self.temp_dir)
            
            if result != 0:
                raise Exception("Failed to repack boot image!")
                
            # Check output
            new_boot_path = os.path.join(self.temp_dir, "new-boot.img")
            if not os.path.exists(new_boot_path):
                raise Exception("Output boot image not found!")
                
            # Calculate SHA256 of patched image
            new_sha256 = self.calculate_sha256(new_boot_path)
            self.log(f"Patched boot SHA256: {new_sha256}", "INFO")
            
            # Save patched image
            self.log("", "")
            self.log("=" * 60)
            self.log("Patching completed successfully!", "SUCCESS")
            self.log("=" * 60)
            
            # Ask where to save
            save_path = filedialog.asksaveasfilename(
                defaultextension=".img",
                filetypes=[("Image files", "*.img"), ("All files", "*.*")],
                initialfile=f"magisk_patched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.img"
            )
            
            if save_path:
                shutil.copy2(new_boot_path, save_path)
                self.log(f"Saved to: {save_path}", "SUCCESS")
                
                # Show success dialog
                size = os.path.getsize(save_path) / (1024 * 1024)
                messagebox.showinfo(
                    "Success",
                    f"Boot image patched successfully!\n\n"
                    f"Output: {os.path.basename(save_path)}\n"
                    f"Size: {size:.2f} MB\n"
                    f"SHA256: {new_sha256[:16]}...\n\n"
                    f"Flash this image to your device's boot partition."
                )
            else:
                self.log("Save cancelled by user", "WARNING")
                
        except Exception as e:
            self.log(f"Error: {str(e)}", "ERROR")
            messagebox.showerror("Patching Failed", f"An error occurred:\n\n{str(e)}")
            
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                    self.log("Cleaned up temporary files", "INFO")
                except:
                    pass
                    
            self.progress.stop()
            self.patch_button.config(state=tk.NORMAL, text="🚀 PATCH")
            self.set_status("Ready")
            self.is_patching = False
            
    def run_command(self, cmd, cwd=None):
        """Run command and capture output"""
        try:
            if isinstance(cmd, str):
                cmd = cmd.split()
                
            # Log command
            self.log(f"$ {' '.join(cmd)}", "DEBUG")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log(line.strip())
                    
            process.wait()
            return process.returncode
            
        except Exception as e:
            self.log(f"Command failed: {str(e)}", "ERROR")
            return -1
            
    def run_command_output(self, cmd, cwd=None):
        """Run command and return output"""
        try:
            if isinstance(cmd, str):
                cmd = cmd.split()
                
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
            return result.stdout.strip()
            
        except Exception as e:
            return ""
            
    def extract_from_apk(self, apk_path, arch, temp_dir):
        """Extract necessary files from Magisk APK"""
        self.log("Extracting files from APK...", "INFO")
        
        needed_files = {}
        
        try:
            with zipfile.ZipFile(apk_path, 'r') as apk:
                # Get Magisk version
                magisk_ver = 0
                magisk_ver_name = ""
                
                try:
                    with apk.open('assets/util_functions.sh') as f:
                        content = f.read().decode('utf-8')
                        
                        # Version code
                        match = re.search(r'MAGISK_VER_CODE=(\d+)', content)
                        if match:
                            magisk_ver = int(match.group(1))
                            
                        # Version name
                        match = re.search(r'MAGISK_VER="([^"]+)"', content)
                        if match:
                            magisk_ver_name = match.group(1)
                            
                    self.log(f"Magisk version: {magisk_ver_name} ({magisk_ver})", "INFO")
                except:
                    self.log("Could not determine Magisk version", "WARNING")
                
                # List all lib files
                available_libs = {}
                for file_info in apk.filelist:
                    if file_info.filename.startswith('lib/') and file_info.filename.endswith('.so'):
                        parts = file_info.filename.split('/')
                        if len(parts) == 3:  # lib/arch/file.so
                            arch_name = parts[1]
                            lib_name = parts[2]
                            
                            if arch_name not in available_libs:
                                available_libs[arch_name] = []
                            available_libs[arch_name].append(lib_name)
                
                self.log(f"Available architectures: {', '.join(available_libs.keys())}", "INFO")
                
                # Extract needed files
                for file_info in apk.filelist:
                    filename = file_info.filename
                    parts = filename.split('/')
                    
                    if len(parts) < 2:
                        continue
                        
                    file_name = parts[-1]
                    parent_dir = parts[-2] if len(parts) > 1 else ""
                    
                    # Handle architecture-specific files
                    if file_name.startswith('lib') and file_name.endswith('.so'):
                        # Skip unnecessary files
                        if file_name in ['libmagiskboot.so', 'libbusybox.so', 'libmagiskpolicy.so']:
                            continue
                            
                        if parent_dir == arch:
                            output_name = file_name.replace('lib', '').replace('.so', '')
                            output_path = os.path.join(temp_dir, output_name)
                            
                            with apk.open(filename) as src, open(output_path, 'wb') as dst:
                                dst.write(src.read())
                                
                            needed_files[output_name] = output_path
                            self.log(f"Extracted: {output_name}", "SUCCESS")
                            
                        # Handle 32-bit compatibility for old Magisk
                        elif magisk_ver < 28000:
                            if arch == "arm64-v8a" and file_name == "libmagisk32.so" and parent_dir == "armeabi-v7a":
                                output_name = "magisk32"
                                output_path = os.path.join(temp_dir, output_name)
                                
                                with apk.open(filename) as src, open(output_path, 'wb') as dst:
                                    dst.write(src.read())
                                    
                                needed_files[output_name] = output_path
                                self.log(f"Extracted: {output_name} (32-bit compat)", "SUCCESS")
                                
                            elif arch == "x86_64" and file_name == "libmagisk32.so" and parent_dir == "x86":
                                output_name = "magisk32"
                                output_path = os.path.join(temp_dir, output_name)
                                
                                with apk.open(filename) as src, open(output_path, 'wb') as dst:
                                    dst.write(src.read())
                                    
                                needed_files[output_name] = output_path
                                self.log(f"Extracted: {output_name} (32-bit compat)", "SUCCESS")
                    
                    # Extract stub.apk
                    elif file_name == "stub.apk":
                        output_path = os.path.join(temp_dir, "stub.apk")
                        
                        with apk.open(filename) as src, open(output_path, 'wb') as dst:
                            dst.write(src.read())
                            
                        needed_files["stub.apk"] = output_path
                        self.log(f"Extracted: stub.apk", "SUCCESS")
                        
                # Check if we got the required files
                required_files = ["magiskinit"]
                missing_files = [f for f in required_files if f not in needed_files]
                
                if missing_files:
                    self.log(f"Missing required files: {', '.join(missing_files)}", "ERROR")
                    
                    # Check if wrong architecture
                    if arch not in available_libs:
                        self.log(f"Architecture {arch} not available in this APK", "ERROR")
                        self.log(f"Try one of: {', '.join(available_libs.keys())}", "WARNING")
                    
                    return None
                    
        except Exception as e:
            self.log(f"Failed to extract from APK: {str(e)}", "ERROR")
            return None
            
        return needed_files
        
    def calculate_sha256(self, filepath):
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

def main():
    # Enable DPI awareness on Windows
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    root = tk.Tk()
    app = MagiskPatcherEnhanced(root)
    root.mainloop()

if __name__ == "__main__":
    main()
