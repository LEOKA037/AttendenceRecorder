# Attendance Recorder

This is a desktop application for recording team attendance.

## Application Features

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

### TAB 3: History
- User selects a **date range**
- Display attendance data in:
  - Clean table view
  - User-friendly readable format
- Now supports editing attendance records.

### TAB 4: Settings
- Add / Edit / Remove:
  - Team Members
  - Attendance Status values
- Changes should reflect immediately in other tabs

### CALENDAR RULES
- Calendar picker must:
  - Allow only weekdays
  - Disable weekends (Saturday & Sunday)

## Build Instructions

To build the executable, you need to have PyInstaller installed.

```
pip install pyinstaller
```

Then, run the following command to build the single-file executable:

```
python -m PyInstaller --onefile --noconsole main.py
```

The executable will be located in the `dist` directory.
