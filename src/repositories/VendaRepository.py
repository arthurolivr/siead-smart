import pandas as pd
from datetime import date
from repositories.database import get_db_engine
from config import get_database_config

def _get_table_name(db_name: str) -> str:
    if db_name.upper() == 'FAMART': return 'venda'
    if db_name.upper() == 'IPB': return 'venda' 
    raise ValueError(f"Nome da tabela de vendas não configurado para o banco: {db_name}")

def fetch_all_sales(db_name: str) -> pd.DataFrame:
    table_name = _get_table_name(db_name)
    engine = get_db_engine(db_name)
    query = f"SELECT data_venda, valor_total FROM {table_name}"
    
    with engine.connect() as connection:
        return pd.read_sql(query, connection)

def fetch_revenue_for_day(target_date: date, db_name: str) -> float:
    table_name = _get_table_name(db_name)
    engine = get_db_engine(db_name)
    query = f"SELECT SUM(valor_total) as revenue FROM {table_name} WHERE data_venda = '{target_date.strftime('%Y-%m-%d')}'"
    
    with engine.connect() as connection:
        result = pd.read_sql(query, connection)
        revenue = result['revenue'].iloc[0]
        return float(revenue) if pd.notna(revenue) else 0.0

def fetch_registration_fee_by_date(target_date: date, db_name: str):
    table_name = _get_table_name(db_name)
    engine = get_db_engine(db_name)
    query = f"""select descricao as type, COUNT(*) as quantity, SUM(pagamento_valor) as value from (
    select cb.descricao, l.pagamento_valor, l.pagamento_data
    from famart--07.venda v
    inner join famart--07.lancamento l on l.venda_id = v.id and l.plano_de_contas_id = 2
    inner join famart--07.conta_bancaria cb on cb.id = l.conta_bancaria_id
    union all
    select cb.descricao, l.pagamento_valor, l.pagamento_data
    from ipb--07.venda v
    inner join ipb--07.lancamento l on l.venda_id = v.id and l.plano_de_contas_id = 2
    inner join ipb--07.conta_bancaria cb on cb.id = l.conta_bancaria_id)
as t
where 1 = 1
and t.pagamento_data between '2025-03-31' and '2025-03-31'"""
    
    with engine.connect() as connection:
        return pd.read_sql(query, connection)
        # fee = result['taxa_matricula'].iloc[0]
       
