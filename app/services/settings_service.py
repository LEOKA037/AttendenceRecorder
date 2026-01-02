from app.storage.repositories import TeamMemberRepository, AttendanceStatusRepository
from app.models import TeamMember, AttendanceStatus

class SettingsService:
    def __init__(self):
        self.member_repository = TeamMemberRepository()
        self.status_repository = AttendanceStatusRepository()

    # Team Member Management
    def add_team_member(self, name):
        if not name:
            raise ValueError("Team member name cannot be empty.")
        if self.member_repository.get_by_name(name):
            raise ValueError(f"Team member '{name}' already exists.")
        member_id = self.member_repository.add({"name": name})
        return TeamMember(member_id, name)

    def get_team_members(self):
        members_data = self.member_repository.get_all()
        return [TeamMember(m['id'], m['name']) for m in members_data]

    def update_team_member(self, member_id, new_name):
        if not new_name:
            raise ValueError("Team member name cannot be empty.")
        existing_member = self.member_repository.get_by_id(member_id)
        if not existing_member:
            raise ValueError(f"Team member with ID {member_id} not found.")
        if self.member_repository.get_by_name(new_name) and existing_member['name'] != new_name:
            raise ValueError(f"Team member '{new_name}' already exists.")
        self.member_repository.update(member_id, {"name": new_name})

    def delete_team_member(self, member_id):
        if not self.member_repository.get_by_id(member_id):
            raise ValueError(f"Team member with ID {member_id} not found.")
        self.member_repository.delete(member_id)

    # Attendance Status Management
    def add_attendance_status(self, status, color="#000000"):
        if not status:
            raise ValueError("Attendance status cannot be empty.")
        if self.status_repository.get_by_status(status):
            raise ValueError(f"Attendance status '{status}' already exists.")
        status_id = self.status_repository.add({"status": status, "color": color})
        return AttendanceStatus(status_id, status, color)

    def get_attendance_statuses(self):
        statuses_data = self.status_repository.get_all()
        return [AttendanceStatus(s['id'], s['status'], s['color']) for s in statuses_data]

    def update_attendance_status(self, status_id, new_status, new_color):
        if not new_status:
            raise ValueError("Attendance status cannot be empty.")
        existing_status = self.status_repository.get_by_id(status_id)
        if not existing_status:
            raise ValueError(f"Attendance status with ID {status_id} not found.")
        if self.status_repository.get_by_status(new_status) and existing_status['status'] != new_status:
            raise ValueError(f"Attendance status '{new_status}' already exists.")
        self.status_repository.update(status_id, {"status": new_status, "color": new_color})

    def delete_attendance_status(self, status_id):
        if not self.status_repository.get_by_id(status_id):
            raise ValueError(f"Attendance status with ID {status_id} not found.")
        self.status_repository.delete(status_id)
