import PyInstaller.__main__
import os
import sys
import customtkinter
from pathlib import Path

def build_exe():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main script
    main_script = os.path.join(script_dir, 'remove_background_new.py')
    
    # Get customtkinter directory
    customtkinter_path = Path(customtkinter.__file__).parent
    
    # Get u2net directory
    u2net_path = os.path.join(os.path.expanduser('~'), '.u2net')
    
    # PyInstaller arguments
    args = [
        main_script,                    # Main script path
        '--onefile',                    # Create a single executable
        '--noconsole',                  # Don't show console window
        '--name=BG_Remover_Pro',        # Name of the executable
        '--clean',                      # Clean cache before building
        f'--add-data={u2net_path}{os.pathsep}u2net',  # Include rembg model files
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=rembg',
        '--hidden-import=customtkinter',
        f'--add-data={customtkinter_path}{os.pathsep}customtkinter',  # Add customtkinter files
    ]
    
    try:
        # Run PyInstaller
        PyInstaller.__main__.run(args)
        print("Build completed successfully!")
        print(f"Executable can be found in {os.path.join(script_dir, 'dist', 'BG_Remover_Pro.exe')}")
    except Exception as e:
        print(f"Error during build: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()
