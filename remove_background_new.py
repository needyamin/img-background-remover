import os
import threading
from tkinter import Tk, Label, Button, filedialog, Canvas, NW, ttk, StringVar, Frame, TclError, messagebox, Menu
from tkinter.messagebox import showinfo, showerror
from PIL import Image, ImageTk
from rembg import remove
import customtkinter as ctk
import requests
import tempfile
import sys
import subprocess
from pathlib import Path
import time
import traceback

# Constants for version checking
CURRENT_VERSION = "1.0.0"  # Update this with your current version
GITHUB_API_URL = "https://api.github.com/repos/needyamin/img-background-remover/releases/latest"
REPO_OWNER = "needyamin"
REPO_NAME = "img-background-remover"

def log(message):
    """Simple logging function"""
    print(f"[LOG] {message}")

def compare_versions(version1, version2):
    """Compare two version strings. Returns True if version1 > version2"""
    def normalize(v):
        return [int(x) for x in v.split(".")]
    try:
        return normalize(version1) > normalize(version2)
    except (AttributeError, TypeError, ValueError):
        return False

class BackgroundRemoverApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Background Remover Pro")
        self.master.geometry("1200x800")
        self.master.configure(bg='#2B2B2B')

        # Create Menu Bar
        self.create_menu_bar()

        # Set up icon for window and taskbar
        try:
            if os.name == 'nt':
                # Set app ID for Windows taskbar
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('mycompany.backgroundremover.1.0')
            
            # Set icon using both methods for maximum compatibility
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "bg_icon.ico")
            if os.path.exists(icon_path):
                self.master.iconbitmap(icon_path)
                self.master.wm_iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not set icon: {e}")
        # Set Windows App ID for taskbar and icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "bg_icon.ico")
            if os.name == 'nt':
                # Set Windows-specific app ID
                import ctypes
                myappid = 'mycompany.backgroundremover.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
            # Set the icon if it exists
            if os.path.exists(icon_path):
                self.master.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not set icon: {e}")
            png_path = os.path.join(base_path, "assets", "bg_icon.png")

            if os.path.exists(png_path):
                # First set the window icon using PNG
                icon = ImageTk.PhotoImage(file=png_path)
                self.master.iconphoto(True, icon)
                self._icon = icon  # Keep reference

                # Ensure ICO exists for taskbar
                if not os.path.exists(ico_path):
                    img = Image.open(png_path)
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    # Save multiple sizes for better quality
                    img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])

                # Set taskbar icon using ICO
                if os.path.exists(ico_path):
                    # Try multiple methods to set the taskbar icon
                    try:
                        self.master.iconbitmap(default=ico_path)
                    except:
                        try:
                            self.master.wm_iconbitmap(ico_path)
                        except:
                            self.master.iconbitmap(ico_path)
                    
                    # Force taskbar refresh
                    self.master.after(100, lambda: [
                        self.master.state('iconic'),
                        self.master.after(100, lambda: self.master.state('normal'))
                    ])
                self._icon = icon  # Keep reference
                
                # Additional Windows-specific handling
                if os.name == 'nt':
                    self.master.after(10, lambda: self.master.state('zoomed') and self.master.state('normal'))
            else:
                print("Icon files not found in assets directory")
        except Exception as e:
            print(f"Could not load application icon: {e}")
        
        # Add keyboard shortcuts
        self.master.bind('<Control-o>', lambda e: self.upload_image())
        self.master.bind('<Control-s>', lambda e: self.save_processed_image())

        # Configure style
        self.style = ttk.Style()
        self.style.configure('Custom.TFrame', background='#2B2B2B')
        self.style.configure('Custom.TLabel', background='#2B2B2B', foreground='white')
        
        # Initialize variables
        self.current_image = None
        self.processed_image = None
        self.original_path = None
        self.status_var = StringVar()
        self.status_var.set("Ready to process images...")
        
        # Create main frame
        self.main_frame = ttk.Frame(master, style='Custom.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Create control panel
        self.control_panel = ttk.Frame(self.main_frame, style='Custom.TFrame')
        self.control_panel.pack(fill='x', pady=(0, 20))

        # Modern styled buttons
        self.upload_button = ctk.CTkButton(
            self.control_panel,
            text="Upload Image",
            command=self.upload_image,
            width=150,
            height=35,
            fg_color="#2185d0",
            hover_color="#1678c2"
        )
        self.upload_button.pack(side='left', padx=5)

        # Save button
        self.save_button = ctk.CTkButton(
            self.control_panel,
            text="Save Image",
            command=self.save_processed_image,
            width=150,
            height=35,
            fg_color="#21ba45",
            hover_color="#16ab39",
            state='disabled'        )
        self.save_button.pack(side='left', padx=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.control_panel,
            mode='indeterminate',
            length=200
        )
        self.progress_bar.pack(side='left', padx=20)

        # Status label
        self.status_label = ttk.Label(
            self.control_panel,
            textvariable=self.status_var,
            style='Custom.TLabel'
        )
        self.status_label.pack(side='left', padx=5)

        # Create image display area
        self.image_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        self.image_frame.pack(fill='both', expand=True)

        # Original image section
        self.original_frame = ttk.Frame(self.image_frame, style='Custom.TFrame')
        self.original_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        self.original_label = ttk.Label(
            self.original_frame,
            text="Original Image",
            style='Custom.TLabel',
            font=('Helvetica', 12, 'bold')
        )
        self.original_label.pack(pady=5)

        self.original_canvas = Canvas(
            self.original_frame,
            width=500,
            height=500,
            bg='#1e1e1e',
            highlightthickness=1,
            highlightbackground="#333333"
        )
        self.original_canvas.pack(pady=5)

        # Processed image section
        self.processed_frame = ttk.Frame(self.image_frame, style='Custom.TFrame')
        self.processed_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        self.removed_label = ttk.Label(
            self.processed_frame,
            text="Background Removed",
            style='Custom.TLabel',
            font=('Helvetica', 12, 'bold')
        )
        self.removed_label.pack(pady=5)

        self.removed_canvas = Canvas(
            self.processed_frame,
            width=500,
            height=500,
            bg='#1e1e1e',
            highlightthickness=1,
            highlightbackground="#333333"
        )
        self.removed_canvas.pack(pady=5)        # Add footer frame
        self.footer_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        self.footer_frame.pack(fill='x', pady=(10, 0))

        # Center container frame
        self.center_frame = ttk.Frame(self.footer_frame, style='Custom.TFrame')
        self.center_frame.pack(expand=True, anchor='center')

        # Credit text before name
        self.credit_prefix = ttk.Label(
            self.center_frame,
            text="Created by ",
            style='Custom.TLabel',
            font=('Helvetica', 10)
        )
        self.credit_prefix.pack(side='left', pady=2)

        # Name with hyperlink
        self.name_link = ttk.Label(
            self.center_frame,
            text="Md. Yamin Hossain",
            style='Custom.TLabel',
            font=('Helvetica', 10, 'underline'),
            cursor="hand2",
            foreground='#2185d0'
        )
        self.name_link.pack(side='left', pady=2)
        self.name_link.bind("<Button-1>", lambda e: self.open_link("https://needyamin.github.io"))

        # Separator
        self.separator = ttk.Label(
            self.center_frame,
            text=" | ",
            style='Custom.TLabel',
            font=('Helvetica', 10)
        )
        self.separator.pack(side='left', pady=2)

        # Github link
        self.github_link = ttk.Label(
            self.center_frame,
            text="Github",
            style='Custom.TLabel',
            font=('Helvetica', 10, 'underline'),
            cursor="hand2",
            foreground='#2185d0'
        )
        self.github_link.pack(side='left', pady=2)
        self.github_link.bind("<Button-1>", lambda e: self.open_link("https://github.com/needyamin/img-background-remover"))        # Set application icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "bg_icon.png")
            if os.path.exists(icon_path):
                # Create PhotoImage for general window icon
                icon_image = ImageTk.PhotoImage(file=icon_path)
                self.master.iconphoto(True, icon_image)
                
                # For Windows taskbar icon
                if os.name == 'nt':  # Windows systems
                    ico_path = self.create_ico_from_png(icon_path)
                    self.master.iconbitmap(default=ico_path)
        except Exception as e:            print(f"Could not load application icon: {e}")

    # Add method to open URLs
    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def open_link(self, url):
        """Open the given URL in the default web browser"""
        import webbrowser
        webbrowser.open(url)

    def create_menu_bar(self):
        """Create the main menu bar"""
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        # File Menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.upload_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Image", command=self.save_processed_image, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        # Edit Menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Images", command=self.clear_images)

        # Help Menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Check for Updates", command=self.check_for_updates)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)

    def clear_images(self):
        """Clear both canvases"""
        self.original_canvas.delete("all")
        self.removed_canvas.delete("all")
        self.current_image = None
        self.processed_image = None
        self.save_button.configure(state='disabled')
        self.status_var.set("Ready to process images...")

    def show_about(self):
        """Show about dialog"""
        about_text = f"""Advanced Background Remover Pro v{CURRENT_VERSION}

Created by Md. Yamin Hossain

This application helps you remove backgrounds from images 
using advanced AI technology.

© 2025 All rights reserved."""
        messagebox.showinfo("About", about_text)

    def upload_image(self, event=None):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if file_path:
            self.process_image(file_path)

    def process_image(self, file_path):
        self.original_path = file_path
        self.status_var.set("Processing image... Please wait...")
        self.progress_bar.start()
        
        def process():
            try:
                # Load and display original image
                original = Image.open(file_path)
                self.current_image = original
                self.display_image(original, self.original_canvas, maintain_aspect=True)

                # Remove background while preserving quality
                output = remove(original)
                self.processed_image = output

                # Display processed image
                self.display_image(output, self.removed_canvas, maintain_aspect=True)
                
                self.master.after(0, lambda: self.status_var.set("Image processed successfully!"))
                self.master.after(0, lambda: self.save_button.configure(state='normal'))
                
            except Exception as e:
                self.master.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                showerror("Error", f"Failed to process image: {str(e)}")
            finally:
                self.master.after(0, self.progress_bar.stop)

        threading.Thread(target=process, daemon=True).start()

    def save_processed_image(self, event=None):
        if self.processed_image is None:
            showerror("Error", "No processed image to save!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile="background_removed.png"
        )
        
        if save_path:
            try:
                # Save with original quality
                self.processed_image.save(save_path, "PNG", quality=100)
                showinfo("Success", "Image saved successfully!")
                self.status_var.set(f"Image saved to: {save_path}")
            except Exception as e:
                showerror("Error", f"Failed to save image: {str(e)}")

    def display_image(self, image, canvas, maintain_aspect=True):
        # Get canvas dimensions
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Calculate scaling factor while maintaining aspect ratio
        if maintain_aspect:
            # Calculate scaling factors for both dimensions
            width_ratio = canvas_width / image.width
            height_ratio = canvas_height / image.height
            
            # Use the smaller ratio to ensure image fits in canvas
            scale_factor = min(width_ratio, height_ratio)
            
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
        else:
            new_width = canvas_width
            new_height = canvas_height

        # Resize image while maintaining quality
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage and display
        tk_image = ImageTk.PhotoImage(resized_image)
        canvas.delete("all")  # Clear previous image
        
        # Center the image in canvas
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2
        
        canvas.image = tk_image  # Keep a reference
        canvas.create_image(x_offset, y_offset, anchor=NW, image=tk_image)

    def create_ico_from_png(self, png_path):
        """Create an ICO file from a PNG file if it doesn't exist"""
        ico_path = png_path.replace('.png', '.ico')
        if not os.path.exists(ico_path):
            try:
                # Open PNG and convert to RGBA if necessary
                img = Image.open(png_path)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Create ICO file with multiple sizes
                icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                img.save(ico_path, format='ICO', sizes=icon_sizes)
            except Exception as e:
                print(f"Could not create ICO file: {e}")
        return ico_path

    def check_for_updates(self):
        """Check for updates on GitHub and return the latest version if available."""
        try:
            log("=== Starting Update Check ===")
            self.status_var.set("Checking for updates...")
            
            # Make the request with headers to avoid rate limiting
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': f'background-remover/{CURRENT_VERSION}'
            }
            
            response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
            log(f"GitHub API Response Status: {response.status_code}")
            
            if response.status_code != 200:
                log(f"GitHub API Error: {response.text}")
                self.status_var.set("Failed to check for updates")
                return None
                
            latest_release = response.json()
            
            # Check if there's a valid release
            if 'tag_name' not in latest_release:
                log("No tag_name found in release")
                self.status_var.set("No updates found")
                return None
                
            # Get the latest version number (strip v prefix if present)
            latest_version = latest_release.get('tag_name', '').lstrip('v')
            log(f"Latest version on GitHub: {latest_version}")
            
            if not latest_version:
                log("Empty version tag found in release")
                self.status_var.set("No valid update found")
                return None
            
            if compare_versions(latest_version, CURRENT_VERSION):
                log(f"New version {latest_version} is available!")
                self.status_var.set(f"New version {latest_version} available!")
                if messagebox.askyesno("Update Available", 
                                     f"Version {latest_version} is available. Would you like to update now?"):
                    self.download_and_install_update(latest_release)
            else:
                log("You have the latest version")
                self.status_var.set("You have the latest version")
                messagebox.showinfo("No Updates", "You have the latest version installed!")
                return None
                
        except requests.exceptions.RequestException as e:
            log(f"Network error checking for updates: {e}")
            self.status_var.set("Network error checking for updates")
            messagebox.showerror("Update Error", f"Network error checking for updates: {e}")
            return None
        except Exception as e:
            log(f"Unexpected error checking for updates: {e}")
            self.status_var.set("Error checking for updates")
            messagebox.showerror("Update Error", f"Error checking for updates: {e}")
            return None

    def download_and_install_update(self, release):
        """Download and install the latest release."""
        try:
            self.status_var.set("Downloading update...")
            latest_version = release.get('tag_name', '').lstrip('v')
            
            # Find the asset with .exe extension
            assets = release.get('assets', [])
            exe_asset = None
            for asset in assets:
                if asset.get('name', '').lower().endswith('.exe'):
                    exe_asset = asset
                    break
                    
            if not exe_asset:
                raise Exception("No executable found in release assets")
            
            # Create temporary directory for download
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                exe_path = temp_path / exe_asset['name']
                
                # Download the new version
                download_url = exe_asset['browser_download_url']
                log(f"Downloading from: {download_url}")
                
                # Show a message to inform the user that download is in progress
                self.status_var.set(f"Downloading version {latest_version}...")
                
                # Download with progress tracking
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(exe_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        downloaded += len(chunk)
                        f.write(chunk)
                
                self.status_var.set("Installing update...")
                
                # Create update script
                update_script = temp_path / "update.bat"
                current_exe = sys.executable
                
                with open(update_script, 'w') as f:
                    f.write(f"""@echo off
echo Waiting for application to close...
timeout /t 2 /nobreak
echo Updating Background Remover...
del "{current_exe}"
if exist "{current_exe}" (
    echo Retrying with force delete...
    taskkill /f /im "{os.path.basename(current_exe)}" 2>nul
    timeout /t 1 /nobreak
    del /f "{current_exe}"
)
echo Copying new version...
copy "{exe_path}" "{current_exe}"
if exist "{current_exe}" (
    echo Starting new version...
    start "" "{current_exe}"
) else (
    echo ERROR: Failed to copy new version.
    pause
)
""")
                
                # Run update script and exit
                subprocess.Popen([str(update_script)], shell=True)
                time.sleep(1)
                sys.exit(0)
                
        except Exception as e:
            error_msg = str(e)
            log(f"Error installing update: {error_msg}")
            self.status_var.set("Update failed")
            messagebox.showerror("Update Error", f"Failed to install update: {error_msg}")
            return False

if __name__ == "__main__":
    root = Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()
