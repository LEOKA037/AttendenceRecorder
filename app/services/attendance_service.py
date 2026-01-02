from app.storage.repositories import AttendanceRecordRepository, TeamMemberRepository, AttendanceStatusRepository
from app.models import AttendanceRecord
from datetime import date, timedelta
import calendar

class AttendanceService:
    def __init__(self):
        self.record_repository = AttendanceRecordRepository()
        self.member_repository = TeamMemberRepository()
        self.status_repository = AttendanceStatusRepository()

    def record_attendance(self, member_id, record_date_str, status_id):
        if not self.member_repository.get_by_id(member_id):
            raise ValueError(f"Team member with ID {member_id} not found.")
        if not self.status_repository.get_by_id(status_id):
            raise ValueError(f"Attendance status with ID {status_id} not found.")
        
        self.record_repository.add_or_update(member_id, record_date_str, status_id)

    def get_attendance_for_date(self, record_date_str):
        attendance_data = self.record_repository.get_attendance_for_date(record_date_str)
        # Convert sqlite3.Row objects to dictionaries or model instances if needed
        return [dict(row) for row in attendance_data]

    def get_attendance_in_date_range(self, start_date_str, end_date_str):
        attendance_data = self.record_repository.get_attendance_in_date_range(start_date_str, end_date_str)
        return [dict(row) for row in attendance_data]

    def get_previous_working_days_attendance(self, num_days=5):
        today = date.today()
        working_days = []
        current_date = today

        while len(working_days) < num_days:
            if current_date.weekday() < 5:  # Monday=0, Sunday=6
                working_days.append(current_date)
            current_date -= timedelta(days=1)
        
        working_days.reverse() # Oldest to newest

        all_members = self.member_repository.get_all()
        na_status = self.status_repository.get_by_status("NA")
        na_status_id = na_status['id'] if na_status else None

        if na_status_id is None:
            raise Exception("'NA' attendance status not found in database. Please ensure it is configured.")

        attendance_summary = {}

        for member in all_members:
            attendance_summary[member['name']] = {}
            for day in working_days:
                attendance_summary[member['name']][day.strftime("%Y-%m-%d")] = "NA" # Default to NA

        for day in working_days:
            date_str = day.strftime("%Y-%m-%d")
            records = self.get_attendance_for_date(date_str)
            for record in records:
                member_name = record['member_name']
                status_name = record['status_name']
                if member_name in attendance_summary:
                    attendance_summary[member_name][date_str] = status_name
        
        # Prepare data for tabular display, ensuring all members are included
        header = ["Team Member"] + [day.strftime("%a %b %d") for day in working_days]
        data_rows = []
        for member_name, daily_attendance in attendance_summary.items():
            row = [member_name]
            for day in working_days:
                row.append(daily_attendance.get(day.strftime("%Y-%m-%d"), "NA"))
            data_rows.append(row)

        statuses = self.get_all_attendance_statuses()
        color_mapping = {status['status']: status['color'] for status in statuses}
        
        return header, data_rows, color_mapping


    def get_all_attendance_statuses(self):
        statuses_data = self.status_repository.get_all()
        return [dict(row) for row in statuses_data]

    def update_attendance_record(self, record_id, new_date, new_status_id):
        """Updates an existing attendance record."""
        if not self.record_repository.get_by_id(record_id):
            raise ValueError(f"Attendance record with ID {record_id} not found.")
        
        update_data = {
            'record_date': new_date,
            'status_id': new_status_id
        }
        self.record_repository.update(record_id, update_data)

