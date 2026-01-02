import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from app.ui.base_tab import BaseTab
from app.services.attendance_service import AttendanceService
from app.utils.image_utils import generate_attendance_image
import os
import csv
import webbrowser
from datetime import date, timedelta, datetime
from tkinter import filedialog
from tkcalendar import DateEntry

class AttendanceImageGeneratorTab(BaseTab):
    def __init__(self, parent, app_instance, *args, **kwargs):
        super().__init__(parent, app_instance, *args, **kwargs)
        self.attendance_service = app_instance.attendance_service
        self.image_tk = None
        self.start_date_var = tk.StringVar(value=(date.today() - timedelta(days=7)).strftime("%Y-%m-%d"))
        self.end_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.logo_path = None
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Generate Attendance Image", font=("Arial", 14)).pack(pady=20)

        # Logo selection
        logo_frame = ttk.Frame(self)
        logo_frame.pack(pady=5)
        ttk.Button(logo_frame, text="Select Logo", command=self._select_logo).pack(side="left", padx=5)
        self.logo_path_label = ttk.Label(logo_frame, text="No logo selected.")
        self.logo_path_label.pack(side="left", padx=5)

        date_range_frame = ttk.Frame(self)
        date_range_frame.pack(pady=10)

        ttk.Label(date_range_frame, text="Start Date:").pack(side="left", padx=5)
        start_date_entry = DateEntry(date_range_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2,
                                         date_pattern='yyyy-mm-dd', textvariable=self.start_date_var)
        start_date_entry.pack(side="left", padx=5)

        ttk.Label(date_range_frame, text="End Date:").pack(side="left", padx=5)
        end_date_entry = DateEntry(date_range_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2,
                                       date_pattern='yyyy-mm-dd', textvariable=self.end_date_var)
        end_date_entry.pack(side="left", padx=5)

        generate_button = ttk.Button(self, text="Generate Image", command=self._generate_image)
        generate_button.pack(pady=10)

        export_button_frame = ttk.Frame(self)
        export_button_frame.pack(pady=5)
        ttk.Button(export_button_frame, text="Export as CSV", command=self._export_csv).pack(side="left", padx=5)
        ttk.Button(export_button_frame, text="Export as PDF", command=self._export_pdf).pack(side="left", padx=5)

        self.output_label = tk.Label(self, text="Generated image will be displayed here.", cursor="hand2")
        self.output_label.pack(pady=5)
        self.output_label.bind("<Button-1>", self._open_image_file)
        self.last_generated_image_path = None # To store the path of the last generated image

    def _select_logo(self):
        path = filedialog.askopenfilename(
            title="Select a Logo",
            filetypes=(("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*"))
        )
        if path:
            self.logo_path = path
            self.logo_path_label.config(text=os.path.basename(path))

    def _export_csv(self):
        try:
            start_date_str = self.start_date_var.get()
            end_date_str = self.end_date_var.get()

            if not start_date_str or not end_date_str:
                messagebox.showerror("Error", "Please select a start and end date.")
                return

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start_date > end_date:
                messagebox.showwarning("Date Range Error", "Start Date cannot be after End Date.")
                return

            header, data_rows, _ = self.attendance_service.get_attendance_for_date_range_for_image(start_date, end_date)
            
            if not data_rows:
                messagebox.showwarning("No Data", "No attendance records for the selected date range.")
                return

            filename = f"attendance_report_{start_date_str}_to_{end_date_str}.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                writer.writerows(data_rows)
            
            messagebox.showinfo("Success", f"Attendance data exported to {os.path.abspath(filename)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")

    def _export_pdf(self):
        # Requires fpdf2: pip install fpdf2
        try:
            from fpdf import FPDF

            start_date_str = self.start_date_var.get()
            end_date_str = self.end_date_var.get()

            if not start_date_str or not end_date_str:
                messagebox.showerror("Error", "Please select a start and end date.")
                return

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start_date > end_date:
                messagebox.showwarning("Date Range Error", "Start Date cannot be after End Date.")
                return

            header, data_rows, color_mapping = self.attendance_service.get_attendance_for_date_range_for_image(start_date, end_date)
            
            if not data_rows:
                messagebox.showwarning("No Data", "No attendance records for the selected date range.")
                return

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, txt="Attendance Report", ln=True, align='C')

            col_widths = [40] + [25] * (len(header) - 1)
            
            # Header
            pdf.set_font("Arial", 'B', 10)
            for i, item in enumerate(header):
                pdf.cell(col_widths[i], 10, item, border=1)
            pdf.ln()

            # Data
            pdf.set_font("Arial", size=10)
            for row in data_rows:
                for i, item in enumerate(row):
                    # Set fill color for status cells
                    if i > 0:
                        if item in color_mapping:
                            hex_color = color_mapping[item].lstrip('#')
                            rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                            pdf.set_fill_color(*rgb_color)
                            fill = True
                        else:
                            fill = False
                    else:
                        fill = False
                    pdf.cell(col_widths[i], 10, item, border=1, fill=fill)
                pdf.ln()

            filename = f"attendance_report_{start_date_str}_to_{end_date_str}.pdf"
            pdf.output(filename)
            
            messagebox.showinfo("Success", f"Attendance data exported to {os.path.abspath(filename)}")

        except ImportError:
            messagebox.showerror("Error", "PDF export requires the 'fpdf2' library. Please install it using: pip install fpdf2")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")

    def _generate_image(self):
        try:
            start_date_str = self.start_date_var.get()
            end_date_str = self.end_date_var.get()

            if not start_date_str or not end_date_str:
                messagebox.showerror("Error", "Please select a start and end date.")
                return

            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format.")
                return

            if start_date > end_date:
                messagebox.showwarning("Date Range Error", "Start Date cannot be after End Date.")
                return

            header, data_rows, color_mapping = self.attendance_service.get_attendance_for_date_range_for_image(start_date, end_date)
            
            if not data_rows:
                messagebox.showwarning("No Data", "No team members found or no attendance records for the selected date range.")
                self.output_label.config(text="No image generated due to missing data.", image='')
                self.image_tk = None
                return

            filename = f"attendance_report_{start_date_str}_to_{end_date_str}.png"
            output_path = generate_attendance_image(header, data_rows, color_mapping, filename, self.logo_path)
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
