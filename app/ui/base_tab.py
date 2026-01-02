import tkinter as tk
from tkinter import ttk

class BaseTab(ttk.Frame):
    def __init__(self, parent, app_instance, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app_instance
        
    def create_widgets(self):
        # This method should be overridden by child classes
        pass

    def on_tab_focus(self):
        """Called when the tab is brought to the foreground."""
        pass

    def on_tab_lose_focus(self):
        """Called when the tab is sent to the background."""
        pass
