from app.storage.database import db

class BaseRepository:
    def __init__(self, table_name):
        self.table_name = table_name

    def _execute(self, query, params=(), fetch_one=False):
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()

    def add(self, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.values()])
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self._execute(query, tuple(data.values()))
        with db.connect() as conn:
            return conn.cursor().lastrowid

    def get_all(self):
        query = f"SELECT * FROM {self.table_name}"
        return self._execute(query)

    def get_by_id(self, item_id):
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        return self._execute(query, (item_id,), fetch_one=True)

    def update(self, item_id, data):
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        params = tuple(data.values()) + (item_id,)
        self._execute(query, params)

    def delete(self, item_id):
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        self._execute(query, (item_id,))


class TeamMemberRepository(BaseRepository):
    def __init__(self):
        super().__init__("team_members")

    def get_by_name(self, name):
        query = f"SELECT * FROM {self.table_name} WHERE name = ?"
        return self._execute(query, (name,), fetch_one=True)


class AttendanceStatusRepository(BaseRepository):
    def __init__(self):
        super().__init__("attendance_statuses")

    def get_by_status(self, status):
        query = f"SELECT * FROM {self.table_name} WHERE status = ?"
        return self._execute(query, (status,), fetch_one=True)


class AttendanceRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__("attendance_records")

    def get_attendance_for_date(self, record_date):
        query = """
            SELECT
                ar.id,
                tm.id AS member_id,
                tm.name AS member_name,
                ar.record_date,
                ast.id AS status_id,
                ast.status AS status_name,
                ar.notes
            FROM attendance_records ar
            JOIN team_members tm ON ar.member_id = tm.id
            JOIN attendance_statuses ast ON ar.status_id = ast.id
            WHERE ar.record_date = ?
        """
        return self._execute(query, (record_date,))

    def get_attendance_for_member_and_date(self, member_id, record_date):
        query = """
            SELECT * FROM attendance_records
            WHERE member_id = ? AND record_date = ?
        """
        return self._execute(query, (member_id, record_date), fetch_one=True)

    def get_attendance_in_date_range(self, start_date, end_date):
        query = """
            SELECT
                ar.id,
                ar.record_date,
                tm.name AS member_name,
                ast.status AS status_name
            FROM attendance_records ar
            JOIN team_members tm ON ar.member_id = tm.id
            JOIN attendance_statuses ast ON ar.status_id = ast.id
            WHERE ar.record_date BETWEEN ? AND ?
            ORDER BY ar.record_date, tm.name
        """
        return self._execute(query, (start_date, end_date))

    def add_or_update(self, member_id, record_date, status_id, notes=None):
        existing_record = self.get_attendance_for_member_and_date(member_id, record_date)
        if existing_record:
            self.update(existing_record['id'], {'status_id': status_id, 'notes': notes})
        else:
            self.add({'member_id': member_id, 'record_date': record_date, 'status_id': status_id, 'notes': notes})

    def bulk_update_status(self, record_ids, status_id):
        if not record_ids:
            return
        placeholders = ', '.join(['?' for _ in record_ids])
        query = f"UPDATE {self.table_name} SET status_id = ? WHERE id IN ({placeholders})"
        params = [status_id] + record_ids
        self._execute(query, params)
