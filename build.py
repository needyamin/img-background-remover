import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def ensure_pyinstaller():
    """Ensure PyInstaller is properly installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            # Remove any leftover .deleteme files first
            scripts_dir = os.path.join(sys.prefix, 'Scripts')
            for file in os.listdir(scripts_dir):
                if file.endswith('.deleteme'):
                    try:
                        os.remove(os.path.join(scripts_dir, file))
                        print(f"Removed leftover file: {file}")
                    except Exception as e:
                        print(f"Warning: Could not remove {file}: {e}")
            
            # Install PyInstaller
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "pyinstaller"])
            time.sleep(2)  # Give some time for file operations to complete
            print("PyInstaller installed successfully")
        except Exception as e:
            print(f"Error installing PyInstaller: {e}")
            sys.exit(1)

def build_exe():
    """Build the executable using PyInstaller"""
    try:
        print("Starting build process...")
        
        # Get the directory of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Script directory: {script_dir}")
        
        # Path to the main script
        main_script = os.path.join(script_dir, 'remove_background_new.py')
        if not os.path.exists(main_script):
            raise FileNotFoundError(f"Main script not found: {main_script}")
        
        # Get u2net directory
        u2net_path = os.path.join(os.path.expanduser('~'), '.u2net')
        if not os.path.exists(u2net_path):
            print("Warning: U2Net model directory not found. It will be downloaded during first run.")
        
        # Get assets directory and verify it exists
        assets_dir = os.path.join(script_dir, 'assets')
        if not os.path.exists(assets_dir):
            raise FileNotFoundError(f"Assets directory not found: {assets_dir}")
        
        # Clean up previous build
        dist_dir = os.path.join(script_dir, 'dist')
        build_dir = os.path.join(script_dir, 'build')
        for dir_path in [dist_dir, build_dir]:
            if os.path.exists(dir_path):
                print(f"Cleaning up {dir_path}")
                shutil.rmtree(dir_path)
        
        # Get customtkinter path for data inclusion
        customtkinter_path = str(Path(customtkinter.__file__).parent)
        
        # PyInstaller arguments
        args = [
            main_script,                    # Main script path
            '--onefile',                    # Create a single executable
            '--noconsole',                  # Don't show console window
            '--name=BG_Remover_Pro',        # Name of the executable
            '--clean',                      # Clean cache before building
            
            # Add data files
            f'--add-data={u2net_path}{os.pathsep}u2net',  # Include rembg model files
            f'--add-data={customtkinter_path}{os.pathsep}customtkinter',  # Include customtkinter files
            f'--add-data={assets_dir}{os.pathsep}assets',  # Include assets folder
            
            # Hidden imports
            '--hidden-import=PIL',
            '--hidden-import=PIL._tkinter_finder',
            '--hidden-import=PIL.ImageQt',
            '--hidden-import=rembg',
            '--hidden-import=customtkinter',
            
            # Add icon
            f'--icon={os.path.join(assets_dir, "bg_icon.ico")}',
            
            # Optimize
            '--noupx',                      # Disable UPX compression
            '--strip',                      # Strip binaries
            '--optimize=2',                 # Python optimization level
        ]
        
        print("\nStarting PyInstaller with arguments:")
        for arg in args:
            print(f"  {arg}")
        
        # Run PyInstaller
        PyInstaller.__main__.run(args)
        
        print("\nBuild completed successfully!")
        print(f"Executable can be found in: {os.path.join(dist_dir, 'BG_Remover_Pro.exe')}")
        
        # Clean up .spec file if it exists
        spec_file = os.path.join(script_dir, 'BG_Remover_Pro.spec')
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print("Cleaned up .spec file")
            
    except Exception as e:
        print(f"\nError during build process: {str(e)}")
        sys.exit(1)

def install_dependencies():
    """Install required dependencies"""
    print("Checking and installing dependencies...")
    dependencies = ['customtkinter']
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"{dep} is already installed")
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", dep])
            print(f"{dep} installed successfully")

if __name__ == '__main__':
    try:
        # Ensure all dependencies are installed
        install_dependencies()
        
        # Ensure PyInstaller is properly installed
        ensure_pyinstaller()
        
        # Import PyInstaller after ensuring it's installed
        import PyInstaller.__main__
        import customtkinter
        
        # Run the build process
        build_exe()
    except KeyboardInterrupt:
        print("\nBuild process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
