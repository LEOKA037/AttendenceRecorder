import tkinter as tk
from tkinter import ttk
from app.ui.base_tab import BaseTab
# Import individual tab implementations here
from app.ui.settings_tab import SettingsTab
from app.ui.daily_standup_entry_tab import DailyStandupEntryTab
from app.ui.attendance_image_generator_tab import AttendanceImageGeneratorTab
from app.ui.history_tab import HistoryTab
from app.services.team_member_service import TeamMemberService
from app.services.attendance_service import AttendanceService
from app.services.settings_service import SettingsService

class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Attendance Recorder")
        self.geometry("1000x700")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Centralized services (dependency injection for tabs)
        self.team_member_service = TeamMemberService()
        self.attendance_service = AttendanceService()
        self.settings_service = SettingsService()

        self._create_tabs()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)


    def _create_tabs(self):
        # Placeholder tabs for now. Will be replaced with actual implementations.
        self.tabs = {}

        self.tabs["Attendance Image Generator"] = AttendanceImageGeneratorTab(self.notebook, self)
        self.notebook.add(self.tabs["Attendance Image Generator"], text="Attendance Image Generator")

        self.tabs["Daily Standup Entry"] = DailyStandupEntryTab(self.notebook, self)
        self.notebook.add(self.tabs["Daily Standup Entry"], text="Daily Standup Entry")

        self.tabs["History"] = HistoryTab(self.notebook, self)
        self.notebook.add(self.tabs["History"], text="History")

        self.tabs["Settings"] = SettingsTab(self.notebook, self)
        self.notebook.add(self.tabs["Settings"], text="Settings")


    def _on_tab_change(self, event):
        selected_tab_id = self.notebook.select()
        selected_tab_widget = self.notebook.nametowidget(selected_tab_id)
        
        # Call on_tab_lose_focus for the previously selected tab
        for tab_name, tab_widget in self.tabs.items():
            if tab_widget is not selected_tab_widget and isinstance(tab_widget, BaseTab):
                tab_widget.on_tab_lose_focus()
        
        # Call on_tab_focus for the newly selected tab
        if isinstance(selected_tab_widget, BaseTab):
            selected_tab_widget.on_tab_focus()

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    app = AttendanceApp()
    app.start()
