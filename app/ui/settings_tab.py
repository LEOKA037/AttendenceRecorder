import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from tkinter import filedialog
import csv
import os
import shutil
import webbrowser
from app.storage.database import DATABASE_FILE
import os
from app.ui.base_tab import BaseTab
from app.services.settings_service import SettingsService

class SettingsTab(BaseTab):
    def __init__(self, parent, app_instance, *args, **kwargs):
        super().__init__(parent, app_instance, *args, **kwargs)
        self.settings_service = SettingsService()
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Paned window to allow resizing
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True)

        # Left frame for members and statuses
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=2)

        # Right frame for database management
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)

        # Frame for Team Members
        member_frame = ttk.LabelFrame(left_frame, text="Manage Team Members")
        member_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.member_listbox = tk.Listbox(member_frame, height=10)
        self.member_listbox.pack(fill="both", expand=True)
        self.member_listbox.bind('<<ListboxSelect>>', self._on_member_select)

        member_entry_frame = ttk.Frame(member_frame)
        member_entry_frame.pack(fill="x", pady=5)
        ttk.Label(member_entry_frame, text="Name:").pack(side="left", padx=5)
        self.member_name_entry = ttk.Entry(member_entry_frame)
        self.member_name_entry.pack(side="left", expand=True, fill="x")

        member_button_frame = ttk.Frame(member_frame)
        member_button_frame.pack(fill="x", pady=5)
        ttk.Button(member_button_frame, text="Add", command=self._add_member).pack(side="left", expand=True)
        ttk.Button(member_button_frame, text="Update", command=self._update_member).pack(side="left", expand=True)
        ttk.Button(member_button_frame, text="Delete", command=self._delete_member).pack(side="left", expand=True)

        member_io_frame = ttk.Frame(member_frame)
        member_io_frame.pack(fill="x", pady=5)
        ttk.Button(member_io_frame, text="Import Members", command=self._import_members).pack(side="left", expand=True)
        ttk.Button(member_io_frame, text="Export Members", command=self._export_members).pack(side="left", expand=True)

        # Frame for Attendance Statuses
        status_frame = ttk.LabelFrame(left_frame, text="Manage Attendance Statuses")
        status_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.status_listbox = tk.Listbox(status_frame, height=10)
        self.status_listbox.pack(fill="both", expand=True)
        self.status_listbox.bind('<<ListboxSelect>>', self._on_status_select)

        status_entry_frame = ttk.Frame(status_frame)
        status_entry_frame.pack(fill="x", pady=5)
        ttk.Label(status_entry_frame, text="Status:").pack(side="left", padx=5)
        self.status_name_entry = ttk.Entry(status_entry_frame)
        self.status_name_entry.pack(side="left", expand=True, fill="x")

        color_entry_frame = ttk.Frame(status_frame)
        color_entry_frame.pack(fill="x", pady=5)
        ttk.Label(color_entry_frame, text="Color:").pack(side="left", padx=5)
        self.status_color_entry = ttk.Entry(color_entry_frame)
        self.status_color_entry.pack(side="left", expand=True, fill="x")
        ttk.Button(color_entry_frame, text="Pick Color", command=self._pick_color).pack(side="left", padx=5)

        status_button_frame = ttk.Frame(status_frame)
        status_button_frame.pack(fill="x", pady=5)
        ttk.Button(status_button_frame, text="Add", command=self._add_status).pack(side="left", expand=True)
        ttk.Button(status_button_frame, text="Update", command=self._update_status).pack(side="left", expand=True)
        ttk.Button(status_button_frame, text="Delete", command=self._delete_status).pack(side="left", expand=True)
        
        status_io_frame = ttk.Frame(status_frame)
        status_io_frame.pack(fill="x", pady=5)
        ttk.Button(status_io_frame, text="Import Statuses", command=self._import_statuses).pack(side="left", expand=True)
        ttk.Button(status_io_frame, text="Export Statuses", command=self._export_statuses).pack(side="left", expand=True)

        # Frame for Database Management
        db_frame = ttk.LabelFrame(right_frame, text="Database Management")
        db_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(db_frame, text="Backup Database", command=self._backup_database).pack(pady=10)
        ttk.Button(db_frame, text="Restore Database", command=self._restore_database).pack(pady=10)

        # About button
        about_button = ttk.Button(right_frame, text="About", command=self._show_about)
        about_button.pack(pady=20)

    def _show_about(self):
        about_window = tk.Toplevel(self)
        about_window.title("About Attendance Recorder")
        about_window.transient(self)
        about_window.grab_set()
        
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Attendance Recorder", font=("Arial", 16, "bold")).pack(pady=5)
        ttk.Label(main_frame, text="Version 1.0").pack(pady=2)
        ttk.Label(main_frame, text="Created by Vibe Coding").pack(pady=10)

        link = ttk.Label(main_frame, text="GitHub Profile", foreground="blue", cursor="hand2")
        link.pack(pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/Vibe-Coding"))

        close_button = ttk.Button(main_frame, text="Close", command=about_window.destroy)
        close_button.pack(pady=10)

    def _backup_database(self):
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                title="Backup Database",
                initialfile="attendance_backup.db"
            )
            if not filepath:
                return

            shutil.copy2(DATABASE_FILE, filepath)
            messagebox.showinfo("Success", f"Database backed up successfully to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to backup database: {e}")

    def _restore_database(self):
        if not messagebox.askyesno("Confirm Restore", "Are you sure you want to restore the database? This will overwrite the current database and the application will need to be restarted."):
            return

        filepath = filedialog.askopenfilename(
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            title="Restore Database"
        )
        if not filepath:
            return

        try:
            # It's a good practice to close the database connection before overwriting the file
            # However, the current architecture does not expose the close method easily.
            # For simplicity, we will just copy the file. The user needs to restart the app anyway.
            shutil.copy2(filepath, DATABASE_FILE)
            messagebox.showinfo("Success", "Database restored successfully. Please restart the application for the changes to take effect.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore database: {e}")

    def _import_members(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import Team Members"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                if header != ["name"]:
                    messagebox.showerror("Error", "Invalid CSV file format for members.")
                    return
                
                imported_count = 0
                skipped_count = 0
                for row in reader:
                    try:
                        self.settings_service.add_team_member(row[0])
                        imported_count += 1
                    except ValueError:
                        skipped_count += 1
            
            self._load_members()
            messagebox.showinfo("Import Complete", f"Imported {imported_count} new team members.\nSkipped {skipped_count} duplicates.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import team members: {e}")

    def _export_members(self):
        members = self.settings_service.get_team_members()
        if not members:
            messagebox.showinfo("No Data", "There are no team members to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Team Members"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["name"])
                for member in members:
                    writer.writerow([member.name])
            messagebox.showinfo("Success", f"Team members exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export team members: {e}")

    def _import_statuses(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import Attendance Statuses"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                if header != ["status", "color"]:
                    messagebox.showerror("Error", "Invalid CSV file format for statuses.")
                    return

                imported_count = 0
                skipped_count = 0
                for row in reader:
                    try:
                        self.settings_service.add_attendance_status(row[0], row[1])
                        imported_count += 1
                    except ValueError:
                        skipped_count += 1
            
            self._load_statuses()
            messagebox.showinfo("Import Complete", f"Imported {imported_count} new statuses.\nSkipped {skipped_count} duplicates.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import statuses: {e}")

    def _export_statuses(self):
        statuses = self.settings_service.get_attendance_statuses()
        if not statuses:
            messagebox.showinfo("No Data", "There are no attendance statuses to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Attendance Statuses"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["status", "color"])
                for status in statuses:
                    writer.writerow([status.status, status.color])
            messagebox.showinfo("Success", f"Attendance statuses exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export attendance statuses: {e}")

    def load_data(self):
        self._load_members()
        self._load_statuses()

    def _load_members(self):
        self.member_listbox.delete(0, tk.END)
        self.team_members = self.settings_service.get_team_members()
        for member in self.team_members:
            self.member_listbox.insert(tk.END, member.name)

    def _load_statuses(self):
        self.status_listbox.delete(0, tk.END)
        self.attendance_statuses = self.settings_service.get_attendance_statuses()
        for status in self.attendance_statuses:
            self.status_listbox.insert(tk.END, status.status)

    def _on_member_select(self, event):
        selected_indices = self.member_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            member_name = self.member_listbox.get(index)
            self.member_name_entry.delete(0, tk.END)
            self.member_name_entry.insert(0, member_name)

    def _on_status_select(self, event):
        selected_indices = self.status_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_status_obj = self.attendance_statuses[index]
            self.status_name_entry.delete(0, tk.END)
            self.status_name_entry.insert(0, selected_status_obj.status)
            self.status_color_entry.delete(0, tk.END)
            self.status_color_entry.insert(0, selected_status_obj.color)

    def _pick_color(self):
        color_code = colorchooser.askcolor(title="Choose color")
        if color_code and color_code[1]:
            self.status_color_entry.delete(0, tk.END)
            self.status_color_entry.insert(0, color_code[1])

    def _add_member(self):
        name = self.member_name_entry.get().strip()
        try:
            self.settings_service.add_team_member(name)
            messagebox.showinfo("Success", f"Team member '{name}' added.")
            self._load_members()
            self.member_name_entry.delete(0, tk.END)
            # Notify other tabs that member list changed (if needed)
            # self.app.notify_member_list_changed()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _update_member(self):
        selected_indices = self.member_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Select a team member to update.")
            return

        index = selected_indices[0]
        selected_member = self.team_members[index]
        new_name = self.member_name_entry.get().strip()

        try:
            self.settings_service.update_team_member(selected_member.id, new_name)
            messagebox.showinfo("Success", f"Team member '{selected_member.name}' updated to '{new_name}'.")
            self._load_members()
            self.member_name_entry.delete(0, tk.END)
            # self.app.notify_member_list_changed()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _delete_member(self):
        selected_indices = self.member_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Select a team member to delete.")
            return

        index = selected_indices[0]
        selected_member = self.team_members[index]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_member.name}'?"):
            try:
                self.settings_service.delete_team_member(selected_member.id)
                messagebox.showinfo("Success", f"Team member '{selected_member.name}' deleted.")
                self._load_members()
                self.member_name_entry.delete(0, tk.END)
                # self.app.notify_member_list_changed()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def _add_status(self):
        status = self.status_name_entry.get().strip()
        color = self.status_color_entry.get().strip()
        try:
            self.settings_service.add_attendance_status(status, color)
            messagebox.showinfo("Success", f"Attendance status '{status}' added.")
            self._load_statuses()
            self.status_name_entry.delete(0, tk.END)
            self.status_color_entry.delete(0, tk.END)
            # self.app.notify_status_list_changed()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _update_status(self):
        selected_indices = self.status_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Select an attendance status to update.")
            return

        index = selected_indices[0]
        selected_status = self.attendance_statuses[index]
        new_status = self.status_name_entry.get().strip()
        new_color = self.status_color_entry.get().strip()

        try:
            self.settings_service.update_attendance_status(selected_status.id, new_status, new_color)
            messagebox.showinfo("Success", f"Attendance status '{selected_status.status}' updated.")
            self._load_statuses()
            self.status_name_entry.delete(0, tk.END)
            self.status_color_entry.delete(0, tk.END)
            # self.app.notify_status_list_changed()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _delete_status(self):
        selected_indices = self.status_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Select an attendance status to delete.")
            return

        index = selected_indices[0]
        selected_status = self.attendance_statuses[index]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_status.status}'?"):
            try:
                self.settings_service.delete_attendance_status(selected_status.id)
                messagebox.showinfo("Success", f"Attendance status '{selected_status.status}' deleted.")
                self._load_statuses()
                self.status_name_entry.delete(0, tk.END)
                # self.app.notify_status_list_changed()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def on_tab_focus(self):
        self.load_data()
