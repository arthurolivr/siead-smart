import pandas as pd
from langchain.agents import tool
from src.utils.app_util import parse_date_range
from src.services.commercial_analysis_service import CommercialAnalysisService
from typing import Literal

@tool
def get_commercial_analysis(
    date_str: str,
    analysis_type: Literal["summary", "team_performance", "agent_performance", "payment_breakdown"],
    db_name: str = "TODOS",
) -> str:
    """
    Ferramenta central e unificada para todas as análises comerciais de matrículas.

    Parâmetros:
    - date_str (obrigatório): O período da análise. Ex: 'hoje', 'mês passado', 'de 01/01/2025 a 15/01/2025'.
    - analysis_type (obrigatório): O tipo de análise a ser feita. Opções:
        - 'summary': Para perguntas sobre totais gerais (quantidade e valor total de matrículas).
        - 'team_performance': Para perguntas sobre ranking ou desempenho de equipes.
        - 'agent_performance': Para perguntas sobre ranking ou desempenho de agenciadores/vendedores.
        - 'payment_breakdown': Para perguntas sobre a distribuição por método de pagamento (PIX, Cartão, Boleto).
    - db_name (opcional, padrão 'TODOS'): A instituição ('FAMART', 'IPB' ou 'TODOS').
    """
    try:
        date_start, date_end = parse_date_range(date_str)
        if not date_start or not date_end:
            return "Não foi possível interpretar o período de data fornecido."

        service = CommercialAnalysisService()
        instituicao: str = f"para {db_name}" if db_name.upper() != 'TODOS' else "para o consolidado (Famart + IPB)"
        periodo_str: str = f"de {date_start:%d/%m/%Y} a {date_end:%d/%m/%Y}"

        if analysis_type == "summary":
            summary = service.get_enrollment_summary(date_start, date_end, db_name)
            return (
                f"📄 Resumo de Matrículas {instituicao} {periodo_str}:\n"
                f"- Quantidade Total: {summary['total_quantity']}\n"
                f"- Valor Total: R$ {summary['total_value']:,.2f}"
            )
        
        elif analysis_type == "team_performance":
            ranking = service.get_performance_ranking(date_start, date_end, db_name, group_by="team")
            if ranking.empty: return "Nenhum dado de desempenho de equipe encontrado para o período."
            return (
                f"🏆 Ranking de Desempenho por Equipe {instituicao} {periodo_str}:\n\n"
                f"{ranking.to_markdown(index=False)}"
            )

        elif analysis_type == "agent_performance":
            ranking = service.get_performance_ranking(date_start, date_end, db_name, group_by="agent")
            if ranking.empty: return "Nenhum dado de desempenho de agenciador encontrado para o período."
            return (
                f"🏆 Ranking de Desempenho por Agenciador {instituicao} {periodo_str} (Top 10):\n\n"
                f"{ranking.head(10).to_markdown(index=False)}"
            )

        elif analysis_type == "payment_breakdown":
            breakdown = service.get_payment_breakdown(date_start, date_end, db_name)
            if breakdown.empty: return "Nenhum dado de método de pagamento encontrado para o período."
            return (
                f"💳 Detalhamento por Método de Pagamento {instituicao} {periodo_str}:\n\n"
                f"{breakdown.to_markdown(index=False)}"
            )
            
        return f"Tipo de análise '{analysis_type}' desconhecido."

    except Exception as e:
        return f"Ocorreu um erro interno ao processar a análise: {e}"