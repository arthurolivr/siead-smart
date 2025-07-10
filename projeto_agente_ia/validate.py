import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import sys

# --- Bloco de Configuração ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'famart',
    'user': 'root',
    'password': '!F@mart+'
}

engine = None
try:
    print("Iniciando processo de validação...")
    
    print("Carregando dados históricos do banco com SQLAlchemy...")
    
    password_encoded = quote_plus(DB_CONFIG['password'])
    db_url = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{password_encoded}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    
    engine = create_engine(db_url)
    query = "SELECT data_venda, valor_total FROM venda"
    df = pd.read_sql(query, engine)
    print("Dados carregados.")

    df['data_venda'] = pd.to_datetime(df['data_venda'])
    df_diario = df.groupby('data_venda')['valor_total'].sum().to_frame()
    
    df_reg = df_diario.copy()
    assert isinstance(df_reg.index, pd.DatetimeIndex)
    df_reg['dia_da_semana'] = df_reg.index.dayofweek
    df_reg['dia_do_mes'] = df_reg.index.day
    df_reg['mes'] = df_reg.index.month
    df_reg['ano'] = df_reg.index.year
    df_reg['semana_do_ano'] = df_reg.index.isocalendar().week.astype(int)
    df_reg['eh_fim_de_mes'] = df_reg.index.is_month_end.astype(int)
    df_reg['venda_dia_anterior'] = df_reg['valor_total'].shift(1).fillna(0)

    dias_para_teste = 30
    dados_de_treino = df_reg[:-dias_para_teste]
    dados_de_teste = df_reg[-dias_para_teste:]

    print(f"\nUsando {len(dados_de_treino)} dias para treinar o modelo.")
    print(f"Usando {len(dados_de_teste)} dias para validar a previsão.")

    X_treino = dados_de_treino.drop('valor_total', axis=1)
    y_treino = dados_de_treino['valor_total']
    X_teste = dados_de_teste.drop('valor_total', axis=1)
    y_real = dados_de_teste['valor_total']

    print("\nTreinando um modelo XGBoost otimizado...")
    modelo_temp = XGBRegressor(
        n_estimators=1000, learning_rate=0.01,
        early_stopping_rounds=5, random_state=42
    )
    modelo_temp.fit(
        X_treino, y_treino,
        eval_set=[(X_teste, y_real)], verbose=False
    )

    print("Fazendo previsões para o período de teste...")
    y_previsto = modelo_temp.predict(X_teste)
    y_previsto = y_previsto.clip(min=0)

    print("\n--- AVALIAÇÃO DO MODELO REFINADO ---")
    df_validacao = pd.DataFrame({'Real': y_real, 'Previsto': y_previsto})
    df_validacao['Diferença'] = df_validacao['Real'] - df_validacao['Previsto']
    df_validacao['Diferença_%'] = (df_validacao['Diferença'] / df_validacao['Real']).replace([float('inf'), -float('inf')], 0) * 100

    mae = mean_absolute_error(y_real, y_previsto)
    print(f"\nO Erro Médio Absoluto (MAE) do modelo é: R$ {mae:,.2f}")
    
    print("\nVisualizando os primeiros 10 dias da validação:")
    print(df_validacao.head(10))

    print("\nGerando gráfico de comparação...")
    plt.figure(figsize=(15, 7))
    plt.plot(df_validacao.index, df_validacao['Real'], label='Faturamento Real', marker='o', linestyle='-')
    plt.plot(df_validacao.index, df_validacao['Previsto'], label='Faturamento Previsto', marker='x', linestyle='--')
    plt.title('Validação do Modelo Otimizado: Faturamento Real vs. Previsto (Últimos 30 Dias)')
    plt.ylabel('Faturamento (R$)')
    plt.xlabel('Data')
    plt.legend()
    plt.grid(True)
    plt.show()

except Exception as e:
    print(f"\nERRO FATAL DURANTE A EXECUÇÃO: {e}")
    sys.exit(1)
finally:
    if engine:
        engine.dispose()
        print("Conexão com o banco de dados encerrada.")