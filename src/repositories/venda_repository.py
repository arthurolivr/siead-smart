import pandas as pd
from datetime import date
from .base_repository import BaseRepository
from src.config.database import db_connection_1

table_name = "venda";

class VendaRepository(BaseRepository):
    def __init__(self):
        super().__init__(db_connection_1.connect)

    def get_all_users(self):
        query = "SELECT * FROM usuario LIMIT 1"
        return self.execute_query(query)

    def fetch_all_sales(self, db_name: str) -> pd.DataFrame:
        query = f"SELECT data_venda, valor_total FROM {table_name}"
        return self.execute_query(query)

    def fetch_revenue_for_day(self, target_date: date, db_name: str) -> float:
        query = f"SELECT SUM(valor_total) as revenue FROM {table_name} WHERE data_venda = '{target_date.strftime('%Y-%m-%d')}'"
        return self.execute_query(query)

    def fetch_registration_fee_by_date(self, date_start: date, date_end: date, db_name: str):
        query = f"""SELECT descricao as type, COUNT(*) as quantity, SUM(pagamento_valor) as value
            FROM (
                SELECT cb.descricao, l.pagamento_valor, l.pagamento_data
                FROM siead07.venda v
                INNER JOIN siead07.lancamento l ON l.venda_id = v.id AND l.plano_de_contas_id = 2
                INNER JOIN siead07.conta_bancaria cb ON cb.id = l.conta_bancaria_id
                
                union all
                
                SELECT cb.descricao, l.pagamento_valor, l.pagamento_data
                FROM siead.venda v
                INNER JOIN siead.lancamento l ON l.venda_id = v.id AND l.plano_de_contas_id = 2
                INNER JOIN siead.conta_bancaria cb ON cb.id = l.conta_bancaria_id)
                as t
            WHERE 1 = 1
            AND t.pagamento_data BETWEEN '{date_start}' AND '{date_end}'
            GROUP BY descricao
            """


        return self.execute_query(query)
