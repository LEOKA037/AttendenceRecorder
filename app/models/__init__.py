class TeamMember:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class AttendanceStatus:
    def __init__(self, id, status, color):
        self.id = id
        self.status = status
        self.color = color

class AttendanceRecord:
    def __init__(self, id, member_id, record_date, status_id):
        self.id = id
        self.member_id = member_id
        self.record_date = record_date
        self.status_id = status_id
