import pandas as pd
from datetime import date
from src.repositories.venda_repository import VendaRepository


class CommercialAnalysisService:
    def __init__(self):
        self.venda_repo = VendaRepository()

    def get_enrollment_analysis(self, date_start: date, date_end: date, db_name: str, team: str | None = None,
                                agent: str | None = None) -> dict:
        """
        Orquestra a busca e análise de dados de matrículas.
        Retorna um dicionário estruturado com o resumo da análise.
        """
        # 1. Busca os dados brutos do repositório
        raw_data = self.venda_repo.fetch_enrollments(
            date_start=date_start,
            date_end=date_end,
            db_name=db_name,
            team_name=team,
            agent_name=agent
        )

        if not raw_data:
            return {"total_quantity": 0, "total_value": 0, "payment_details": []}

        # 2. Usa o Pandas para facilitar a agregação e análise
        df = pd.DataFrame(raw_data)

        # 3. Calcula os totais
        total_quantity = len(df)
        total_value = df['pagamento_valor'].sum()

        # 4. Cria o detalhamento por método de pagamento
        payment_details_df = df.groupby('descricao').agg(
            quantity=('pagamento_valor', 'count'),
            value=('pagamento_valor', 'sum')
        ).reset_index()

        payment_details = payment_details_df.rename(columns={'descricao': 'type'}).to_dict('records')

        # 5. Retorna o resultado estruturado
        return {
            "total_quantity": total_quantity,
            "total_value": total_value,
            "payment_details": payment_details
        }