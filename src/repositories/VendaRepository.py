import pandas as pd
from datetime import date
from .database import get_db_engine

TABELA = "venda"

def fetch_all_sales() -> pd.DataFrame:
    engine = get_db_engine()
    query = f"SELECT data_venda, valor_total FROM {TABELA}"
    try:
        with engine.connect() as connection:
            return pd.read_sql(query, connection)
    finally:
        engine.dispose()

def fetch_revenue_for_day(target_date: date) -> float:
    engine = get_db_engine()
    query = f"""
        SELECT SUM(valor_total) as revenue 
        FROM {TABELA}
        WHERE data_venda = '{target_date.strftime('%Y-%m-%d')}'
    """
    try:
        with engine.connect() as connection:
            result = pd.read_sql(query, connection)
            revenue_value = result['revenue'].iloc[0]
            return float(revenue_value) if pd.notna(revenue_value) else 0.0
    except Exception as e:
        print(f"Error fetching revenue for {target_date}: {e}")
        return 0.0
    finally:
        engine.dispose()