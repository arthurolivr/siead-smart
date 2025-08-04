from .base_repository import BaseRepository
from src.config.database import db_connection_1

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(db_connection_1.connect)

    def get_all_users(self):
        query = "SELECT * FROM usuario LIMIT 1"
        return self.execute_query(query)