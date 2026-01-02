You are an expert Python desktop application developer.

Generate a **lightweight Windows desktop application using Python** with the following requirements:

========================
GENERAL REQUIREMENTS
========================
- OS: Windows
- Language: Python
- UI Framework: Lightweight (prefer Tkinter; PySide6 acceptable if justified)
- Architecture:
  - Follow SOLID principles
  - Clean package structure
  - Separate files for UI, services, models, storage, and utils
- Storage:
  - Local storage only
  - Use SQLite or file-based storage (JSON/CSV)
- Build:
  - Provide instructions to generate a single `.exe` using PyInstaller
- Code Quality:
  - Simple, readable, well-commented
  - Modular and extensible
- App should support multiple users (user configurable)

========================
APPLICATION FEATURES
========================

### TAB 1: Attendance Image Generator
- Button to generate attendance image for **previous 5 working days**
- If continuous 5 days data is NOT available:
  - Show a clear message indicating missing dates
  - Still allow image generation
  - Missing values should be filled as **"NA"**
- Generated output:
  - Image format (PNG/JPG)
  - Clean tabular layout
  - Saved locally
- Preview in the tab and on click of preview open the image in a new window

---

### TAB 2: Daily Standup Entry
- User inputs attendance for team members
- Attendance dropdown values:
  - Work From Home
  - On Time
  - Late
  - NA
- Dropdown values must be configurable from **Settings Tab**
- Date:
  - Default = today
  - User can change date
  - If data exists for selected date → auto-load values
- Save data locally

---

### TAB 3: History
- User selects a **date range**
- Display attendance data in:
  - Clean table view
  - User-friendly readable format
- Filter by user and status
- editing feature on double click

---

### TAB 4: Settings
- Add / Edit / Remove:
  - Team Members
  - Attendance Status values with color maping
- Changes should reflect immediately in other tabs

---

### CALENDAR RULES
- Calendar picker must:
  - Allow only weekdays
  - Disable weekends (Saturday & Sunday)

---

### TECHNICAL EXPECTATIONS
- Follow SOLID principles
- Proper folder structure (example):
app/
ui/
services/
models/
storage/
utils/
main.py
- Use classes and interfaces where applicable
- Avoid hardcoding values
- Include basic validation and error handling

---

### BUILD OUTPUT
- Provide:
- PyInstaller command
- Any required config
- Output:
- Single executable (.exe)
- No console window
- Works on Windows without Python installed

---

### DELIVERABLES
1. Full Python source code
2. Folder structure
3. Explanation of design
4. PyInstaller build steps
5. Notes on extending features later

Generate the complete solution accordingly.

---

### Automated Build and Test

After making code changes, you can use the `build_and_test.ps1` script to automatically test if the application starts correctly and then build the executable.

To run the script, open a PowerShell terminal and execute the following command:

```powershell
.\build_and_test.ps1
```

The script will:
1.  Start the application (`main.py`).
2.  Wait for 10 seconds to check for any immediate crashes.
3.  If the application is still running, it will proceed to build the single-file executable using PyInstaller.
4.  After a successful build, it will prompt you to manually check the functionality of the generated `.exe` file located in the `dist` directory.

If the application crashes during the 10-second window, the script will abort and notify you to debug the issue manually.