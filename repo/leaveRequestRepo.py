from repo.BaseRepo import BaseRepo

class LeaveRequestRepo(BaseRepo):
    def __init__(self):
        super().__init__("leaveRequests")
        
        