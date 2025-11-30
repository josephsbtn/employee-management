from repo.BaseRepo import BaseRepo

class AttendanceRepo(BaseRepo):
    def __init__(self):
        super().__init__("attendances")
        
        