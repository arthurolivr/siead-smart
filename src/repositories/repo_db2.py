from .base_repository import BaseRepository
from src.config.database import db_connection_2

class SalesRepository(BaseRepository):
    def __init__(self):
        super().__init__(db_connection_2.connect)

    def get_recent_sales(self, limit=10):
        query = "SELECT * FROM venda ORDER BY data_venda DESC LIMIT %s"
        return self.execute_query(query, (limit,))