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
        self.attendance_entries = {} # {member_id: {'status': StringVar, 'notes': StringVar}}
        self.mark_all_status_var = tk.StringVar()
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

        # Mark all as frame
        mark_all_frame = ttk.Frame(self.attendance_frame)
        mark_all_frame.pack(fill="x", pady=5)
        ttk.Label(mark_all_frame, text="Mark all as:").pack(side="left", padx=5)
        
        statuses = self.attendance_service.get_all_attendance_statuses()
        status_options = [s['status'] for s in statuses]
        self.mark_all_combo = ttk.Combobox(mark_all_frame, textvariable=self.mark_all_status_var, values=status_options, state="readonly")
        self.mark_all_combo.pack(side="left", padx=5)
        if status_options:
            self.mark_all_status_var.set(status_options[0])
            
        ttk.Button(mark_all_frame, text="Apply", command=self._mark_all_as).pack(side="left", padx=5)

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

    def _mark_all_as(self):
        selected_status = self.mark_all_status_var.get()
        if not selected_status:
            messagebox.showwarning("Warning", "Please select a status to apply.")
            return

        for entry in self.attendance_entries.values():
            entry['status'].set(selected_status)

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

        # Header
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill="x", pady=2)
        ttk.Label(header_frame, text="Team Member", width=20, anchor="w", font='TkDefaultFont 9 bold').pack(side="left", padx=5)
        ttk.Label(header_frame, text="Status", width=20, anchor="w", font='TkDefaultFont 9 bold').pack(side="left", padx=5)
        ttk.Label(header_frame, text="Notes", width=40, anchor="w", font='TkDefaultFont 9 bold').pack(side="left", padx=5)


        for member in members:
            row_frame = ttk.Frame(self.scrollable_frame)
            row_frame.pack(fill="x", pady=2)
            ttk.Label(row_frame, text=f"{member.name}:", width=20, anchor="w").pack(side="left", padx=5)
            
            # Status Dropdown
            status_var = tk.StringVar(row_frame)
            if status_options:
                status_var.set(status_options[0]) # Default to first status or "NA"
            
            option_menu = ttk.OptionMenu(row_frame, status_var, status_var.get(), *status_options)
            option_menu.pack(side="left", fill="x", expand=True, padx=5)

            # Notes Entry
            notes_var = tk.StringVar(row_frame)
            notes_entry = ttk.Entry(row_frame, textvariable=notes_var, width=40)
            notes_entry.pack(side="left", fill="x", expand=True, padx=5)

            self.attendance_entries[member.id] = {'status': status_var, 'notes': notes_var}
        
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_data_for_selected_date(self):
        selected_date_str = self.selected_date.get()
        records = self.attendance_service.get_attendance_for_date(selected_date_str)
        
        # Create a dictionary for quick lookup: {member_id: {'status_name': str, 'notes': str}}
        current_attendance = {record['member_id']: {'status_name': record['status_name'], 'notes': record['notes']} for record in records}
        
        statuses = self.attendance_service.get_all_attendance_statuses()
        status_map = {s['status']: s['id'] for s in statuses} # {status_name: status_id}

        members = self.team_member_service.get_all_members()

        # Update the OptionMenu and Notes for each member
        for member in members:
            if member.id in self.attendance_entries:
                entry = self.attendance_entries[member.id]
                if member.id in current_attendance:
                    entry['status'].set(current_attendance[member.id]['status_name'])
                    entry['notes'].set(current_attendance[member.id]['notes'] or "")
                else:
                    # Default to 'NA' if available, otherwise first option
                    if "NA" in status_map:
                        entry['status'].set("NA")
                    elif statuses:
                         entry['status'].set(statuses[0]['status'])
                    entry['notes'].set("")

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
            members = {m.id: m.name for m in self.team_member_service.get_all_members()}
            
            summary = "Attendance Summary:\n"
            for member_id, entry in self.attendance_entries.items():
                member_name = members.get(member_id, f"ID: {member_id}")
                summary += f"- {member_name}: {entry['status'].get()} (Notes: {entry['notes'].get()})\n"

            if messagebox.askyesno("Confirm Save", summary + "\nDo you want to save this attendance?"):
                for member_id, entry in self.attendance_entries.items():
                    status_name = entry['status'].get()
                    notes = entry['notes'].get()
                    status_id = status_map.get(status_name)
                    if status_id is None:
                        messagebox.showerror("Error", f"Invalid status selected for member ID {member_id}: {status_name}")
                        return
                    self.attendance_service.record_attendance(member_id, selected_date_str, status_id, notes)
                messagebox.showinfo("Success", f"Attendance saved for {selected_date_str}.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("An error occurred", str(e))

    def on_tab_focus(self):
        # When this tab gets focus, refresh team members and statuses
        self.update_attendance_entries()
        self.load_data_for_selected_date()
