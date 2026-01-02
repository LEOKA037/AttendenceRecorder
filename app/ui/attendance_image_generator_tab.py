import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from app.ui.base_tab import BaseTab
from app.services.attendance_service import AttendanceService
from app.utils.image_utils import generate_attendance_image
import os
import webbrowser

class AttendanceImageGeneratorTab(BaseTab):
    def __init__(self, parent, app_instance, *args, **kwargs):
        super().__init__(parent, app_instance, *args, **kwargs)
        self.attendance_service = app_instance.attendance_service
        self.image_tk = None
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Generate Attendance Image for Previous 5 Working Days", font=("Arial", 14)).pack(pady=20)

        generate_button = ttk.Button(self, text="Generate Image", command=self._generate_image)
        generate_button.pack(pady=10)

        self.output_label = tk.Label(self, text="Generated image will be displayed here.", cursor="hand2")
        self.output_label.pack(pady=5)
        self.output_label.bind("<Button-1>", self._open_image_file)
        self.last_generated_image_path = None # To store the path of the last generated image

    def _generate_image(self):
        try:
            header, data_rows, color_mapping = self.attendance_service.get_previous_working_days_attendance()
            
            if not data_rows:
                messagebox.showwarning("No Data", "No team members found or no attendance records for the last 5 working days.")
                self.output_label.config(text="No image generated due to missing data.", image='')
                self.image_tk = None
                return

            filename = f"attendance_report_{self.app.selected_date.get() if hasattr(self.app, 'selected_date') else 'current'}.png"
            output_path = generate_attendance_image(header, data_rows, color_mapping, filename)
            self.last_generated_image_path = os.path.abspath(output_path)

            # Display the image
            img = Image.open(self.last_generated_image_path)
            
            # Resize image to fit in the window nicely
            max_width = 600
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            self.image_tk = ImageTk.PhotoImage(img)
            self.output_label.config(image=self.image_tk, text="") # Show image, clear text
            messagebox.showinfo("Success", f"Attendance image generated successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate image: {str(e)}")
            self.output_label.config(text=f"Error: {str(e)}", image='')
            self.image_tk = None
            self.last_generated_image_path = None

    def _open_image_file(self, event=None):
        if self.last_generated_image_path and os.path.exists(self.last_generated_image_path):
            try:
                # Use webbrowser.open for cross-platform compatibility
                webbrowser.open(f"file://{self.last_generated_image_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
        elif self.last_generated_image_path:
            messagebox.showwarning("File Not Found", f"The image file was not found at: {self.last_generated_image_path}")
