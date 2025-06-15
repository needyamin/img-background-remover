import os
import threading
from tkinter import Tk, Label, Button, filedialog, Canvas, NW, ttk, StringVar, Frame, TclError
from tkinter.messagebox import showinfo, showerror
from PIL import Image, ImageTk
from rembg import remove
import customtkinter as ctk

class BackgroundRemoverApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Background Remover Pro")
        self.master.geometry("1200x800")
        self.master.configure(bg='#2B2B2B')
        
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
            state='disabled'
        )
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
        self.removed_canvas.pack(pady=5)

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

if __name__ == "__main__":
    root = Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()
