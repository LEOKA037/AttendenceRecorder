# Attendance Recorder
# Created by: VIBE CODING
This is a desktop application for recording team attendance.

## Application Features

### TAB 1: Attendance Image Generator
- Generates attendance image for **previous 5 working days**
- Generated output:
  - Image format JPG
  - Clean tabular layout
  - Saved locally
- Preview in the tab and on click of preview open the image in a new window

### TAB 2: Daily Standup Entry
- User inputs attendance for team members and selects dropdown values
- User/Dropdown values are configurable from **Settings Tab**
- Date:
  - Default = today
  - User can change date
  - If data exists for selected date → auto-load values
- Save data locally

### TAB 3: History
- User selects a **date range** and results are displayed
- Filter by user and status
- Editing feature on double click

### TAB 4: Settings
- Add / Edit / Remove:
  - Team Members
  - Attendance Status values with color codes
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
