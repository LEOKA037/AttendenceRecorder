import tkinter as tk
from tkinter import ttk
import json
import os
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

        self.config = self._load_config()
        self._create_tabs()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _load_config(self):
        config_path = "config.json"
        default_config = {
            "tab_order": [
                "Attendance Image Generator",
                "Daily Standup Entry",
                "History",
                "Settings"
            ]
        }
        if not os.path.exists(config_path):
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        else:
            with open(config_path, 'r') as f:
                return json.load(f)

    def _create_tabs(self):
        self.tabs = {}
        tab_classes = {
            "Attendance Image Generator": AttendanceImageGeneratorTab,
            "Daily Standup Entry": DailyStandupEntryTab,
            "History": HistoryTab,
            "Settings": SettingsTab
        }

        tab_order = self.config.get("tab_order", [])

        for tab_name in tab_order:
            if tab_name in tab_classes:
                tab_class = tab_classes[tab_name]
                self.tabs[tab_name] = tab_class(self.notebook, self)
                self.notebook.add(self.tabs[tab_name], text=tab_name)


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
