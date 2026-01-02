import tkinter as tk
from tkinter import ttk, messagebox
from app.ui.base_tab import BaseTab
from app.services.attendance_service import AttendanceService
from app.utils.date_utils import is_weekday
from datetime import datetime, date, timedelta
from tkcalendar import DateEntry # Requires pip install tkcalendar

class HistoryTab(BaseTab):
    def __init__(self, parent, app_instance, *args, **kwargs):
        super().__init__(parent, app_instance, *args, **kwargs)
        self.attendance_service = app_instance.attendance_service
        self.team_member_service = app_instance.team_member_service # Added to get members for filter
        self.start_date_var = tk.StringVar(value=(date.today() - timedelta(days=7)).strftime("%Y-%m-%d"))
        self.end_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.filter_member_var = tk.StringVar(value="All")
        self.filter_status_var = tk.StringVar(value="All")
        self.full_history_data = [] # To store all data for the selected date range
        self.edit_button = None
        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        # Date range selection
        date_range_frame = ttk.Frame(self)
        date_range_frame.pack(pady=10)

        ttk.Label(date_range_frame, text="Start Date:").pack(side="left", padx=5)
        self.start_date_entry = DateEntry(date_range_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2,
                                         date_pattern='yyyy-mm-dd', textvariable=self.start_date_var)
        self.start_date_entry.pack(side="left", padx=5)
        self.start_date_entry.bind("<<DateEntrySelected>>", self._on_date_change)
        self.start_date_var.trace_add("write", self._on_date_change)
        
        ttk.Label(date_range_frame, text="End Date:").pack(side="left", padx=5)
        self.end_date_entry = DateEntry(date_range_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2,
                                       date_pattern='yyyy-mm-dd', textvariable=self.end_date_var)
        self.end_date_entry.pack(side="left", padx=5)
        self.end_date_entry.bind("<<DateEntrySelected>>", self._on_date_change)
        self.end_date_var.trace_add("write", self._on_date_change)
        
        ttk.Button(date_range_frame, text="Load History", command=self.load_history).pack(side="left", padx=10)

        # Filter widgets
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Filter by Member:").pack(side="left", padx=5)
        self.member_filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_member_var, state="readonly")
        self.member_filter_combo.pack(side="left", padx=5)
        self.member_filter_combo.bind("<<ComboboxSelected>>", self._apply_filters)

        ttk.Label(filter_frame, text="Filter by Status:").pack(side="left", padx=5)
        self.status_filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_status_var, state="readonly")
        self.status_filter_combo.pack(side="left", padx=5)
        self.status_filter_combo.bind("<<ComboboxSelected>>", self._apply_filters)

        # Attendance data display (Treeview)
        self.tree = ttk.Treeview(self, columns=("Date", "Team Member", "Status"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Team Member", text="Team Member")
        self.tree.heading("Status", text="Status")

        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Team Member", width=150, anchor="w")
        self.tree.column("Status", width=100, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._open_edit_window)

        # Edit button
        self.edit_button = ttk.Button(self, text="Edit Selected", command=self._open_edit_window, state="disabled")
        self.edit_button.pack(pady=5)

    def _on_tree_select(self, event=None):
        if self.tree.selection():
            self.edit_button.config(state="normal")
        else:
            self.edit_button.config(state="disabled")

    def _open_edit_window(self, event=None):
        if not self.tree.selection():
            return

        record_id = self.tree.selection()[0]
        
        # Find the full record details from self.full_history_data
        selected_record = None
        for record in self.full_history_data:
            if str(record['id']) == record_id:
                selected_record = record
                break
                
        if not selected_record:
            messagebox.showerror("Error", "Could not find the selected record's details.")
            return
        
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Attendance Record")
        edit_window.transient(self) # Keep edit window on top of the main app
        edit_window.grab_set() # Modal behavior

        main_frame = ttk.Frame(edit_window, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Date
        ttk.Label(main_frame, text="Date:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        date_var = tk.StringVar(value=selected_record['record_date'])
        date_entry = DateEntry(main_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd', textvariable=date_var)
        date_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Member Name (read-only)
        ttk.Label(main_frame, text="Team Member:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(main_frame, text=selected_record['member_name']).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Status
        ttk.Label(main_frame, text="Status:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        status_var = tk.StringVar(value=selected_record['status_name'])
        statuses = self.attendance_service.get_all_attendance_statuses()
        status_names = [s['status'] for s in statuses]
        status_map = {s['status']: s['id'] for s in statuses}
        status_combo = ttk.Combobox(main_frame, textvariable=status_var, values=status_names, state="readonly")
        status_combo.grid(row=2, column=1, padx=10, pady=5)
        
        def _save_changes():
            try:
                new_date = date_var.get()
                new_status_name = status_var.get()
                new_status_id = status_map[new_status_name]
                
                self.attendance_service.update_attendance_record(record_id, new_date, new_status_id)
                messagebox.showinfo("Success", "Record updated successfully.", parent=edit_window)
                edit_window.destroy()
                self.load_history() # Refresh the view
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update record: {e}", parent=edit_window)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        save_button = ttk.Button(button_frame, text="Save", command=_save_changes)
        save_button.pack(side="left", padx=10)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=edit_window.destroy)
        cancel_button.pack(side="left", padx=10)

    def _on_date_change(self, *args):
        self.load_history()

    def load_history(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        start_date_str = self.start_date_var.get()
        end_date_str = self.end_date_var.get()

        if not start_date_str or not end_date_str:
            return # Do not load history if dates are empty

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format.")
            return

        if start_date > end_date:
            messagebox.showwarning("Date Range Error", "Start Date cannot be after End Date.")
            return

        history_data = self.attendance_service.get_attendance_in_date_range(start_date_str, end_date_str)
        self.full_history_data = history_data
        self._populate_filters()
        self._apply_filters()

    def _populate_filters(self):
        members = ["All"] + [member.name for member in self.team_member_service.get_all_members()]
        self.member_filter_combo['values'] = members
        self.filter_member_var.set("All")

        statuses = ["All"] + [status['status'] for status in self.attendance_service.get_all_attendance_statuses()]
        self.status_filter_combo['values'] = statuses
        self.filter_status_var.set("All")

    def _apply_filters(self, event=None):
        for i in self.tree.get_children():
            self.tree.delete(i)

        filtered_data = self.full_history_data
        selected_member = self.filter_member_var.get()
        selected_status = self.filter_status_var.get()

        if selected_member != "All":
            filtered_data = [row for row in filtered_data if row['member_name'] == selected_member]

        if selected_status != "All":
            filtered_data = [row for row in filtered_data if row['status_name'] == selected_status]

        for record in filtered_data:
            self.tree.insert("", "end", iid=record['id'], values=(record['record_date'], record['member_name'], record['status_name']))

    def on_tab_focus(self):
        self.load_history()
        self._populate_filters()
