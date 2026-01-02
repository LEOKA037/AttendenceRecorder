from tkcalendar import DateEntry
import tkinter as tk
from tkinter import ttk, messagebox
from app.ui.base_tab import BaseTab
from app.services.attendance_service import AttendanceService
from app.services.team_member_service import TeamMemberService
from app.utils.date_utils import is_weekday
from datetime import date, datetime

class DailyStandupEntryTab(BaseTab):
    def __init__(self, parent, app_instance, *args, **kwargs):
        super().__init__(parent, app_instance, *args, **kwargs)
        self.attendance_service = app_instance.attendance_service
        self.team_member_service = app_instance.team_member_service
        self.selected_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.attendance_entries = {} # {member_id: StringVar for status}
        self.create_widgets()
        self.load_data_for_selected_date()

    def create_widgets(self):
        # Date selection
        date_frame = ttk.Frame(self)
        date_frame.pack(pady=10)

        ttk.Label(date_frame, text="Select Date:").pack(side="left", padx=5)
        self.date_entry = DateEntry(date_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2,
                                     date_pattern='yyyy-mm-dd', textvariable=self.selected_date)
        self.date_entry.pack(side="left", padx=5)
        self.date_entry.bind("<<DateEntrySelected>>", self._on_date_change)
        self.selected_date.trace_add("write", self._on_date_change)

        # Attendance entry frame
        self.attendance_frame = ttk.LabelFrame(self, text="Team Attendance")
        self.attendance_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(self.attendance_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.scrollbar = ttk.Scrollbar(self.attendance_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.update_attendance_entries()

        # Save button
        ttk.Button(self, text="Save Attendance", command=self._save_attendance).pack(pady=10)

    def _on_date_change(self, *args):
        self.load_data_for_selected_date()

    def update_attendance_entries(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.attendance_entries.clear()

        members = self.team_member_service.get_all_members()
        statuses = self.attendance_service.get_all_attendance_statuses()
        status_options = [s['status'] for s in statuses]
        
        if not members:
            ttk.Label(self.scrollable_frame, text="No team members configured. Please go to Settings tab to add team members.").pack(pady=10)
            return

        for member in members:
            row_frame = ttk.Frame(self.scrollable_frame)
            row_frame.pack(fill="x", pady=2)
            ttk.Label(row_frame, text=f"{member.name}:", width=20, anchor="w").pack(side="left", padx=5)
            
            # StringVar to hold the selected status for this member
            status_var = tk.StringVar(row_frame)
            if status_options:
                status_var.set(status_options[0]) # Default to first status or "NA"
            
            option_menu = ttk.OptionMenu(row_frame, status_var, status_var.get(), *status_options)
            option_menu.pack(side="left", fill="x", expand=True, padx=5)
            self.attendance_entries[member.id] = status_var
        
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_data_for_selected_date(self):
        selected_date_str = self.selected_date.get()
        records = self.attendance_service.get_attendance_for_date(selected_date_str)
        
        # Create a dictionary for quick lookup: {member_id: status_name}
        current_attendance = {record['member_id']: record['status_name'] for record in records}
        
        statuses = self.attendance_service.get_all_attendance_statuses()
        status_map = {s['status']: s['id'] for s in statuses} # {status_name: status_id}

        members = self.team_member_service.get_all_members()

        # Update the OptionMenu for each member
        for member in members:
            if member.id in self.attendance_entries:
                status_var = self.attendance_entries[member.id]
                if member.id in current_attendance:
                    status_var.set(current_attendance[member.id])
                else:
                    # Default to 'NA' if available, otherwise first option
                    if "NA" in status_map:
                        status_var.set("NA")
                    elif status_var.get() not in status_map and statuses:
                         status_var.set(statuses[0]['status'])

    def _save_attendance(self):
        selected_date_str = self.selected_date.get()
        try:
            # Validate if selected date is a weekday (re-check in case of manual input)
            selected_dt = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            if not is_weekday(selected_dt):
                messagebox.showwarning("Invalid Date", "Attendance can only be saved for weekdays.")
                return

            statuses = self.attendance_service.get_all_attendance_statuses()
            status_map = {s['status']: s['id'] for s in statuses}

            for member_id, status_var in self.attendance_entries.items():
                status_name = status_var.get()
                status_id = status_map.get(status_name)
                if status_id is None:
                    messagebox.showerror("Error", f"Invalid status selected for member ID {member_id}: {status_name}")
                    return
                self.attendance_service.record_attendance(member_id, selected_date_str, status_id)
            messagebox.showinfo("Success", f"Attendance saved for {selected_date_str}.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("An error occurred", str(e))

    def on_tab_focus(self):
        # When this tab gets focus, refresh team members and statuses
        self.update_attendance_entries()
        self.load_data_for_selected_date()
