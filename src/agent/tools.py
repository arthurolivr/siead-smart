import pandas as pd
from langchain.agents import tool
from src.utils.app_util import parse_date_range
from src.utils.logger import get_logger
from src.services.commercial_analysis_service import CommercialAnalysisService

logger = get_logger("deploy")


@tool
def analyze_enrollments(
        date_str: str,
        db_name: str,
        team: str = None,
        agent: str = None,
        detailed: bool = False
) -> str:
    """
    Analisa matrículas pagas em um período e retorna um relatório completo. É a ferramenta principal para todas as perguntas sobre desempenho de matrículas.

    CAPACIDADES OBRIGATÓRIAS DESTA FERRAMENTA:
    - DETALHAMENTO: Para detalhar os totais por método de pagamento (PIX, Cartão, Boleto), você DEVE definir o parâmetro 'detailed' como True.
    - FILTROS: Esta ferramenta PODE E DEVE ser usada para filtrar por equipe ou agenciador. Use os parâmetros 'team' e 'agent' quando o usuário mencioná-los.
    - PERÍODO: O parâmetro 'date_str' aceita datas únicas (ex: 'hoje', '2025-09-01') ou intervalos (ex: 'de 2025-09-01 a 2025-09-07').

    Parâmetros:
    - date_str (obrigatório): A data ou período da análise. Ex: 'hoje', 'ontem', 'de 01/07/2025 a 15/07/2025'.
    - db_name (obrigatório): A instituição ('FAMART', 'IPB' ou 'TODOS').
    - team (opcional): O nome EXATO de uma equipe para filtrar os resultados. Ex: 'Equipe Comercial Gold'.
    - agent (opcional): O nome EXATO de um agenciador para filtrar os resultados.
    - detailed (opcional): Defina como True para obter o detalhamento por método de pagamento.
    """
    logger.info(">>> INÍCIO DA EXECUÇÃO DA FERRAMENTA DE ANÁLISE DE MATRÍCULAS <<<")

    try:
        date_start, date_end = parse_date_range(date_str)
        if not date_start or not date_end:
            return "Não consegui entender o período informado. Por favor, especifique a data ou o intervalo."

        logger.info(
            f"Analisando período de {date_start} a {date_end} para DB: {db_name}, Equipe: {team}, Agenciador: {agent}")

        service = CommercialAnalysisService()
        analysis = service.get_enrollment_analysis(date_start, date_end, db_name, team, agent)

        if analysis['total_quantity'] == 0:
            return f"Nenhuma matrícula encontrada para os filtros selecionados no período de {date_start:%d/%m/%Y} a {date_end:%d/%m/%Y}."

        instituicao = f"para a instituição {db_name}" if db_name.upper() != 'TODOS' else "para o consolidado (Famart + IPB)"

        filtros_str = []
        if team: filtros_str.append(f"equipe '{team}'")
        if agent: filtros_str.append(f"agenciador '{agent}'")
        filtro_info = f" com filtro para {', '.join(filtros_str)}" if filtros_str else ""

        resposta = (
            f"Análise de matrículas de {date_start:%d/%m/%Y} a {date_end:%d/%m/%Y} {instituicao}{filtro_info}:\n"
            f"----------------------------------------\n"
            f"📈 **Quantidade Total:** {analysis['total_quantity']} matrículas\n"
            f"💰 **Valor Total:** R$ {analysis['total_value']:,.2f}\n"
        )

        if detailed and analysis['payment_details']:
            resposta += "\n**Detalhes por método de pagamento:**\n"
            payment_map = {
                'PIX': ['PIX - SIEAD', 'PIX – CONTA CORRENTE'],
                'CARTÃO': ['CARTÃO - SIEAD', 'CARTÃO – SAFRA PAY', 'CARTÃO - ORENDA'],
                'BOLETO': ['BOLETO - SIEAD']
            }

            summary = {'PIX': {'quantity': 0, 'value': 0.0}, 'CARTÃO': {'quantity': 0, 'value': 0.0},
                       'BOLETO': {'quantity': 0, 'value': 0.0}}
            for detail in analysis['payment_details']:
                for category, descriptions in payment_map.items():
                    if detail['type'] in descriptions:
                        summary[category]['quantity'] += int(detail['quantity'])
                        summary[category]['value'] += detail['value']
                        break

            for category, data in summary.items():
                if data['quantity'] > 0:
                    resposta += f"- {category}: {data['quantity']} matrículas, totalizando R$ {data['value']:,.2f}\n"

        return resposta

    except Exception as e:
        logger.error(f"Erro ao executar a análise de matrículas: {e}")
        return f"Ocorreu um erro interno ao processar sua solicitação: {e}"