from repo.BaseRepo import BaseRepo


class ShiftsRepo(BaseRepo):
    def __init__(self):
        super().__init__("shifts")  