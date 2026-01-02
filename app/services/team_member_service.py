from app.storage.repositories import TeamMemberRepository
from app.models import TeamMember

class TeamMemberService:
    def __init__(self):
        self.repository = TeamMemberRepository()

    def add_member(self, name):
        if not name:
            raise ValueError("Team member name cannot be empty.")
        if self.repository.get_by_name(name):
            raise ValueError(f"Team member '{name}' already exists.")
        member_id = self.repository.add({"name": name})
        return TeamMember(member_id, name)

    def get_all_members(self):
        members_data = self.repository.get_all()
        return [TeamMember(m['id'], m['name']) for m in members_data]

    def update_member(self, member_id, new_name):
        if not new_name:
            raise ValueError("Team member name cannot be empty.")
        existing_member = self.repository.get_by_id(member_id)
        if not existing_member:
            raise ValueError(f"Team member with ID {member_id} not found.")
        if self.repository.get_by_name(new_name) and existing_member['name'] != new_name:
            raise ValueError(f"Team member '{new_name}' already exists.")
        self.repository.update(member_id, {"name": new_name})

    def delete_member(self, member_id):
        if not self.repository.get_by_id(member_id):
            raise ValueError(f"Team member with ID {member_id} not found.")
        self.repository.delete(member_id)
