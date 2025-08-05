import pandas as pd
from langchain.agents import tool
from src.repositories.venda_repository import VendaRepository
from src.utils.app_util import parse_date_range
from src.utils.logger import get_logger

logger = get_logger("deploy")

@tool
def get_registration_fees(date_str: str, db_name: str) -> str:
    """
    Usa o banco de dados real da instituição para consultar taxas de matrícula pagas.
    Retorna dados formatados com total, quantidade e métodos de pagamento por data.
    Deve ser usada sempre que o usuário perguntar sobre matrículas ou valores pagos.
    Use esta ferramenta para perguntas sobre 'taxa de matrícula', 'matrículas pagas', ou 'inscrições'.

    Parâmetros:
    - date_str: Data no formato ISO (YYYY-MM-DD) para a consulta.
    - db_name: Nome do banco de dados ('FAMART', 'IPB' ou 'TODOS').
    """

    logger.info(">>> INÍCIO DA EXECUÇÃO <<<")

    try:
        date_start, date_end = parse_date_range(date_str)
        if not date_start or not date_end:
            return "Não consegui entender a data informada."

        logger.info("Data inicio: %s", date_start)
        logger.info("Data fim: %s", date_end)

        repo = VendaRepository()
        result = repo.fetch_registration_fee_by_date(date_start, date_end, db_name)
        logger.info("result: %s", result)
        summary_df = pd.DataFrame(result)

        logger.info("DataFrame: %s", summary_df)

        if summary_df.empty:
            return f"Não foram encontradas taxas de matrícula para {db_name} na data {date_str}."
        
        total_value = summary_df['value'].sum()
        instituicao = f"A instituição {db_name}" if db_name.upper() != 'TODOS' else "o consolidado (Famart + IPB)"
        
        details = "\n".join(
            f"- {row['type']}: {int(row['quantity'])} registros, totalizando R$ {row['value']:,.2f}"
            for _, row in summary_df.iterrows()
        )
        
        return (
            f"Relatório de taxas de matrícula para {instituicao} de {date_start:%d/%m/%Y} até {date_end:%d/%m/%Y}:\n"
            f"----------------------------------------\n"
            f"Valor Total: R$ {total_value:,.2f}\n"
            f"Detalhes por Conta:\n{details}"
        )
    except Exception as e:
        return f"Ocorreu um erro ao buscar taxas de matrícula para {db_name} na data {date_str}: {e}"
