from datetime import date
from typing import Any, Literal
from .base_repository import BaseRepository
from src.config.database import db_connection_1
from dotenv import load_dotenv
import os

load_dotenv()
database_famart: str | None = os.getenv("DB1_DATABASE")
database_ipb: str | None = os.getenv("DB2_DATABASE")

if not database_famart or not database_ipb:
    raise ValueError("Variáveis de ambiente DB1_DATABASE ou DB2_DATABASE não foram encontradas.")

class VendaRepository(BaseRepository):
    def __init__(self):
        super().__init__(db_connection_1.connect)

    def fetch_enrollment_data(
        self, 
        date_start: date, 
        date_end: date, 
        db_name: str,
        group_by: Literal["team", "agent", "payment_method"] | None = None
    ) -> list[dict]:
        """
        Função unificada e segura para buscar dados de matrículas.
        Pode retornar dados brutos ou agrupados por equipe, agenciador ou método de pagamento.
        """
        assert database_famart is not None
        assert database_ipb is not None

        def _get_base_query(db: str):
            return f"""
                SELECT
                    cb.descricao as payment_method,
                    l.pagamento_valor as value,
                    l.pagamento_data as payment_date,
                    e.nome AS team_name,
                    a.nome AS agent_name
                FROM {db}.venda v
                INNER JOIN {db}.lancamento l ON l.venda_id = v.id AND l.plano_de_contas_id = 2
                INNER JOIN {db}.conta_bancaria cb ON cb.id = l.conta_bancaria_id
                INNER JOIN {db}.usuario u ON v.vendedor_id = u.id
                INNER JOIN {db}.agenciador a ON a.usuario_id = u.id
                LEFT JOIN {db}.equipe_usuario eu ON eu.usuario_id = u.id
                LEFT JOIN {db}.equipe e ON e.id = eu.equipe_id
            """

        if db_name.upper() == "IPB":
            subquery: str = _get_base_query(database_ipb)
        elif db_name.upper() == "FAMART":
            subquery = _get_base_query(database_famart)
        else:
            subquery = f"({_get_base_query(database_famart)}) UNION ALL ({_get_base_query(database_ipb)})"
        
        params: dict[str, Any] = {'date_start': date_start, 'date_end': date_end}
        where_clause = "WHERE t.payment_date BETWEEN %(date_start)s AND %(date_end)s"

        if group_by:
            group_by_column = ""
            if group_by == "team":
                group_by_column = "team_name"
            elif group_by == "agent":
                group_by_column = "agent_name"
            elif group_by == "payment_method":
                group_by_column = "payment_method"
            
            query: str = f"""
                SELECT 
                    {group_by_column} as name,
                    COUNT(*) as quantity,
                    SUM(t.value) as total_value
                FROM ({subquery}) as t
                {where_clause}
                GROUP BY {group_by_column}
                ORDER BY total_value DESC
            """
        else: # Se não agrupar, retorna os dados brutos
            query = f"SELECT * FROM ({subquery}) as t {where_clause}"

        return self.execute_query(query, params)