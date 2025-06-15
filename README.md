# Image Background Remover Pro

A modern desktop application that removes backgrounds from images with high quality results. Built with Python and customtkinter, this tool provides a user-friendly interface for quick and efficient background removal.

![Image Background Remover Pro](https://github.com/user-attachments/assets/4376158e-1333-4781-91c1-ea84503d6cac)

## Features

- Modern dark-themed user interface
- High-quality background removal using rembg
- Maintains original image quality
- Simple drag & drop interface
- Quick keyboard shortcuts
- Automatic image scaling while maintaining aspect ratio
- Progress indicator for processing status

## Download

Download the latest standalone executable:
[BG_Remover_Pro.exe](https://github.com/needyamin/img-background-remover/releases/download/v1.0.0/BG_Remover_Pro.exe)

## Usage

1. Launch the application
2. Click "Upload Image" or use Ctrl+O to select an image
3. Wait for processing to complete
4. Save the processed image using the "Save" button or Ctrl+S

## Keyboard Shortcuts

- `Ctrl+O`: Open/Upload image
- `Ctrl+S`: Save processed image

## Building from Source

### Requirements
```
rembg>=2.0.0
pillow>=10.0.0
onnxruntime>=1.15.0
customtkinter>=5.2.0
pyinstaller
```

### Build Steps
1. Clone the repository
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the build script:
   ```bash
   python build.py
   ```
4. Find the executable in the `dist` folder

## Technical Details

- Built with Python 3.x
- Uses rembg for background removal
- CustomTkinter for modern UI elements
- PyInstaller for creating standalone executable
- Preserves original image quality throughout processing

## License

[MIT License](LICENSE)

## Author

[Md. Yamin Hossain](https://github.com/needyamin)
