from repo.BaseRepo import BaseRepo

class HistoryRepo(BaseRepo):
    def __init__(self):
        super().__init__("histories")