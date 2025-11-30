from repo.BaseRepo import BaseRepo

class AnnualRequestRepo(BaseRepo):
    def __init__(self):
        super().__init__("annualRequests")
        
        