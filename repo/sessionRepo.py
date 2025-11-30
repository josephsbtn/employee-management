from repo.BaseRepo import BaseRepo

class SessionRepo(BaseRepo):
    def __init__(self):
        super().__init__("sessions")