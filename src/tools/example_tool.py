from src.repositories.repo_db1 import UserRepository
from src.repositories.repo_db2 import SalesRepository

class ExampleTool:
    def __init__(self):
        self.user_repo = UserRepository()
        self.sales_repo = SalesRepository()

    def run(self):
        users = self.user_repo.get_all_users()
        sales = self.sales_repo.get_recent_sales()
        return {
            "users_count": len(users),
            "latest_sale": sales[0] if sales else None
        }