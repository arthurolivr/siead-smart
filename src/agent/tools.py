from langchain.agents import tool
from datetime import date, timedelta
from ..services.PredictionService import predict_daily_revenue, summarize_long_term_forecast

@tool
def predict_revenue_for_specific_date(date_str: str) -> str:
    """Use esta ferramenta para prever o faturamento de um único dia específico. A data DEVE ser uma string no formato 'AAAA-MM-DD'."""
    try:
        target_date = date.fromisoformat(date_str)
        revenue = predict_daily_revenue(target_date)
        return f"A previsão de faturamento para {target_date.strftime('%d/%m/%Y')} é de R$ {revenue:,.2f}."
    except ValueError:
        return "Formato de data inválido. Por favor, use 'AAAA-MM-DD'."

@tool
def summarize_revenue_forecast(days: int) -> str:
    """Use esta ferramenta para obter um resumo da previsão de faturamento para um período futuro em dias. Use-a para perguntas sobre 'próximos X dias', 'próximo mês' (30 dias), etc."""
    summary = summarize_long_term_forecast(days)
    return (f"Para os próximos {days} dias, a previsão é de um faturamento total de R$ {summary['total_revenue']:,.2f}, "
            f"com uma média diária de R$ {summary['daily_average']:,.2f}.")

@tool
def predict_revenue_for_tomorrow() -> str:
    """Use esta ferramenta quando o usuário perguntar especificamente sobre a previsão de 'amanhã'."""
    target_date = date.today() + timedelta(days=1)
    return predict_revenue_for_specific_date(target_date.strftime('%Y-%m-%d'))