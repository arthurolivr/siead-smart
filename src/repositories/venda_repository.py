import pandas as pd
from datetime import date
from .base_repository import BaseRepository
from src.config.database import db_connection_1
from dotenv import load_dotenv
import os

load_dotenv()
database_famart = os.getenv(f"DB1_DATABASE")
database_ipb = os.getenv(f"DB2_DATABASE")


class VendaRepository(BaseRepository):
    def __init__(self):
        super().__init__(db_connection_1.connect)

    def _get_base_enrollments_query(self, db_name: str):
        """
        Query base REUTILIZÁVEL que busca os dados essenciais de matrículas,
        incluindo pagamento, equipe e agenciador. Fica em um método privado.
        """
        return f"""
            SELECT
                cb.descricao,
                l.pagamento_valor,
                l.pagamento_data,
                e.nome AS nome_equipe,
                a.nome AS nome_agenciador
            FROM {db_name}.venda v
            INNER JOIN {db_name}.lancamento l ON l.venda_id = v.id AND l.plano_de_contas_id = 2
            INNER JOIN {db_name}.conta_bancaria cb ON cb.id = l.conta_bancaria_id
            INNER JOIN {db_name}.usuario u ON v.vendedor_id = u.id
            INNER JOIN {db_name}.agenciador a ON a.usuario_id = u.id
            LEFT JOIN {db_name}.equipe_usuario eu ON eu.usuario_id = u.id
            LEFT JOIN {db_name}.equipe e ON e.id = eu.equipe_id
        """

    def fetch_enrollments(self, date_start: date, date_end: date, db_name: str, team_name: str | None = None,
                          agent_name: str | None = None) -> list[dict]:
        """
        Busca dados brutos de matrículas em um período, com filtros opcionais.
        Esta função busca os dados detalhados para serem processados pela camada de serviço.
        """
        if db_name.upper() == "IPB":
            subquery = self._get_base_enrollments_query(database_ipb)
        elif db_name.upper() == "FAMART":
            subquery = self._get_base_enrollments_query(database_famart)
        else:
            subquery = f"""
                ({self._get_base_enrollments_query(database_famart)})
                UNION ALL
                ({self._get_base_enrollments_query(database_ipb)})
            """

        where_conditions = ["t.pagamento_data BETWEEN %(date_start)s AND %(date_end)s"]
        params = {'date_start': date_start, 'date_end': date_end}

        if team_name:
            where_conditions.append("t.nome_equipe = %(team_name)s")
            params['team_name'] = team_name

        if agent_name:
            where_conditions.append("t.nome_agenciador = %(agent_name)s")
            params['agent_name'] = agent_name

        where_clause = " AND ".join(where_conditions)

        query = f"""
            SELECT *
            FROM ({subquery}) AS t
            WHERE {where_clause}
        """

        return self.execute_query(query, params)