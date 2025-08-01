from repositories.VendaRepository import fetch_registration_fee_by_date
from langchain.agents import tool
from datetime import date, timedelta
from services.PredictionService import predict_daily_revenue, summarize_long_term_forecast

@tool
def predict_revenue_for_specific_date(date_str: str, db_name: str) -> str:
    """
    Retorna a previsão de faturamento para uma data específica e instituição.

    Parâmetros:
    - date_str: Data no formato ISO (YYYY-MM-DD) para previsão.
    - db_name: Nome do banco de dados ('FAMART', 'IPB' ou 'TODOS').

    Retorna uma string resumindo a previsão de faturamento para a data.
    """
    try:
        target_date = date.fromisoformat(date_str)
        revenue = predict_daily_revenue(target_date, db_name)
        instituicao = (
            f"a instituição {db_name}"
            if db_name.upper() != 'TODOS'
            else "o consolidado (Famart + IPB)"
        )
        return f"Para {instituicao}, a previsão em {target_date:%d/%m/%Y} é de R$ {revenue:,.2f}."
    except Exception as e:
        return f"Ocorreu um erro ao prever para {db_name}: {e}"

@tool
def summarize_revenue_forecast(days: int, db_name: str) -> str:
    """
    Gera um resumo da previsão de faturamento para um período futuro.

    Parâmetros:
    - days: Número de dias à frente para sumarização.
    - db_name: Nome do banco de dados ('FAMART', 'IPB' ou 'TODOS').

    Retorna uma string com total previsto e média diária.
    """
    try:
        summary = summarize_long_term_forecast(days, db_name)
        instituicao = (
            f"a instituição {db_name}"
            if db_name.upper() != 'TODOS'
            else "o consolidado (Famart + IPB)"
        )
        return (
            f"Para {instituicao}, a previsão nos próximos {days} dias é de um faturamento total de R$ {summary['total_revenue']:,.2f}, "
            f"com média diária de R$ {summary['daily_average']:,.2f}."
        )
    except Exception as e:
        return f"Ocorreu um erro ao resumir a previsão para {db_name}: {e}"

@tool
def predict_revenue_for_tomorrow(db_name: str) -> str:
    """
    Previsão de faturamento para o dia seguinte.

    Parâmetros:
    - db_name: Nome do banco de dados ('FAMART', 'IPB' ou 'TODOS').

    Retorna uma string com a previsão de faturamento para amanhã.
    """
    try:
        target_date = date.today() + timedelta(days=1)
        revenue = predict_daily_revenue(target_date, db_name)
        instituicao = (
            f"a instituição {db_name}"
            if db_name.upper() != 'TODOS'
            else "o consolidado (Famart + IPB)"
        )
        return f"Para {instituicao}, a previsão para amanhã ({target_date:%d/%m/%Y}) é de R$ {revenue:,.2f}."
    except Exception as e:
        return f"Ocorreu um erro ao prever para amanhã para {db_name}: {e}"
    
@tool
def get_registration_fees(date_str: str, db_name: str) -> str:
    """
    Busca o total e os detalhes das taxas de matrícula pagas em uma data específica.
    Use esta ferramenta para perguntas sobre 'taxa de matrícula', 'matrículas pagas', ou 'inscrições'.

    Parâmetros:
    - date_str: Data no formato ISO (YYYY-MM-DD) para a consulta.
    - db_name: Nome do banco de dados ('FAMART', 'IPB' ou 'TODOS').
    """
    try:
        target_date = date.fromisoformat(date_str)
        summary_df = fetch_registration_fee_by_date(target_date, db_name)
        
        if summary_df.empty:
            return f"Não foram encontradas taxas de matrícula para {db_name} na data {date_str}."
        
        total_value = summary_df['value'].sum()
        instituicao = f"a instituição {db_name}" if db_name.upper() != 'TODOS' else "o consolidado (Famart + IPB)"
        
        details = "\n".join(
            f"- {row['type']}: {int(row['quantity'])} registros, totalizando R$ {row['value']:,.2f}"
            for _, row in summary_df.iterrows()
        )
        
        return (
            f"Relatório de taxas de matrícula para {instituicao} em {target_date:%d/%m/%Y}:\n"
            f"----------------------------------------\n"
            f"Valor Total Arrecadado: R$ {total_value:,.2f}\n"
            f"Detalhes por Conta:\n{details}"
        )
    except Exception as e:
        return f"Ocorreu um erro ao buscar taxas de matrícula para {db_name} na data {date_str}: {e}"