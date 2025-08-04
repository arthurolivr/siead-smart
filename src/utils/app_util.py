import dateparser
from typing import Tuple, Optional
from datetime import date, datetime

def parse_date_range(text: str) -> Tuple[Optional[date], Optional[date]]:
    """
    Interpreta expressões de data como:
    - 'hoje'
    - 'ontem'
    - 'do dia 01/07 a 31/07'
    - 'últimos 7 dias'
    - '1 de agosto de 2025'
    Retorna (data_inicial, data_final)
    """
    texto = text.lower()

    # Tenta detectar dois períodos
    if " a " in texto or " até " in texto:
        delimitador = " a " if " a " in texto else " até "
        partes = texto.split(delimitador)
        start = dateparser.parse(partes[0])
        end = dateparser.parse(partes[1])
    else:
        # Data única
        parsed = dateparser.parse(texto)
        start = end = parsed

    if start:
        start = start.date()
    if end:
        end = end.date()

    return start, end