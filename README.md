# Attendance Recorder
# Created by: VIBE CODING
This is a desktop application for recording team attendance.

## Tech Stack
- **Python**: Core language
- **Tkinter**: GUI framework
- **SQLite**: Local database
- **Pillow**: Image manipulation
- **fpdf2**: PDF generation
- **PyInstaller**: Executable builder
- **tkcalendar**: Calendar widget

## Application Features

### TAB 1: Attendance Image Generator
- Generate attendance image for a **custom date range**.
- **Export** attendance data as **PDF** or **CSV**.
- Add a **company logo** to the generated image.
- Preview the generated image in the tab.
- Click the preview to open the image in the default viewer.
- Generated output is saved locally as a JPG image.

### TAB 2: Daily Standup Entry
- User inputs attendance for team members.
- **"Mark all as..."** to quickly set status for all members.
- Add **notes** for each attendance entry.
- Shows a **confirmation prompt** before saving.
- Dropdown values for status are configurable from the **Settings Tab**.
- Date defaults to today, but can be changed.
- Auto-loads existing data for the selected date.
- Saves data locally.

### TAB 3: History
- Display attendance data for a selected **date range**.
- **Sort** data by clicking on column headers.
- **Search** for specific records.
- **Filter** by team member and status.
- **Edit** a single record by double-clicking.
- **Bulk edit** multiple records at once.

### TAB 4: Settings
- **Manage Team Members**: Add, Edit, Delete.
- **Manage Attendance Statuses**: Add, Edit, Delete, with color codes.
- **Import/Export**: Manage team members and statuses from/to CSV files.
- **Database Management**: Backup and restore the application database.
- **About**: View application details.
- Changes reflect immediately in other tabs.

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