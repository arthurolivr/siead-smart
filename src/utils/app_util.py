import dateparser
import re
import calendar
from typing import Tuple, Optional
from datetime import date, datetime

def parse_date_range(text: str) -> Tuple[Optional[date], Optional[date]]:
    """
    Interpreta expressões de data, agora com suporte a trimestres e semanas em português.
    """
    texto = text.lower()
    start_dt: Optional[datetime] = None
    end_dt: Optional[datetime] = None
    
    date_settings = {'DATE_ORDER': 'YMD', 'PREFER_DAY_OF_MONTH': 'first'}

    # Lógica para trimestres
    match_trimestre = re.search(r'(primeiro|segundo|terceiro|quarto)\s+trimestre\s+de\s+(\d{4})', texto)
    if match_trimestre:
        trimestre_str, ano_str = match_trimestre.groups()
        ano = int(ano_str)
        trimestres = {
            "primeiro": (date(ano, 1, 1), date(ano, 3, 31)),
            "segundo": (date(ano, 4, 1), date(ano, 6, 30)),
            "terceiro": (date(ano, 7, 1), date(ano, 9, 30)),
            "quarto": (date(ano, 10, 1), date(ano, 12, 31)),
        }
        return trimestres.get(trimestre_str, (None, None))

    # --- NOVA LÓGICA PARA SEMANAS ---
    meses = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
        'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    match_semana = re.search(r'(primeira|segunda|terceira|quarta)\s+semana\s+de\s+([a-zA-Zç]+)\s+de\s+(\d{4})', texto)
    if match_semana:
        semana_str, mes_str, ano_str = match_semana.groups()
        ano = int(ano_str)
        mes = meses.get(mes_str)
        if mes:
            semanas = {
                "primeira": (date(ano, mes, 1), date(ano, mes, 7)),
                "segunda": (date(ano, mes, 8), date(ano, mes, 14)),
                "terceira": (date(ano, mes, 15), date(ano, mes, 21)),
            }
            if semana_str in semanas:
                return semanas[semana_str]
            elif semana_str == "quarta":
                ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
                return (date(ano, mes, 22), date(ano, mes, ultimo_dia_mes))
    # --- FIM DA NOVA LÓGICA ---

    # Lógica principal de parsing
    if " a " in texto or " até " in texto:
        delimitador = " a " if " a " in texto else " até "
        partes = texto.split(delimitador)
        parte_inicial = partes[0].replace('de', '').strip()
        parte_final = partes[1].strip()
        start_dt = dateparser.parse(parte_inicial, languages=['pt'], settings=date_settings)
        end_dt = dateparser.parse(parte_final, languages=['pt'], settings=date_settings)
    else:
        parsed_dt = dateparser.parse(texto, languages=['pt'], settings=date_settings)
        start_dt = end_dt = parsed_dt

    start_date = start_dt.date() if start_dt else None
    end_date = end_dt.date() if end_dt else None

    return start_date, end_date