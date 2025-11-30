from repo.BaseRepo import BaseRepo
class EmployeeRepo(BaseRepo):
    def __init__(self):
        super().__init__("employees")
    