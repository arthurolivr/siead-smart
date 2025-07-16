# scripts/train_model.py (Versão Final com Correção do Prophet)

import sys
import os
import pandas as pd
from xgboost import XGBRegressor
from prophet import Prophet
import pickle

# Adiciona a pasta raiz do projeto ao mapa de busca do Python.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.siead_smart.repositories.sales_repository import fetch_all_sales
from src.siead_smart.config import MODELS_DIR, SHORT_TERM_MODEL_PATH, LONG_TERM_MODEL_PATH

try:
    print("Starting the training process...")
    print("Fetching sales data from the data layer...")
    df = fetch_all_sales()
    print("Data fetched successfully. Preparing features...")

    df['sale_date'] = pd.to_datetime(df['data_venda'])
    daily_df = df.groupby('sale_date')['valor_total'].sum().to_frame(name='total_revenue')
    
    regression_df = daily_df.copy()
    assert isinstance(regression_df.index, pd.DatetimeIndex)

    regression_df['day_of_week'] = regression_df.index.dayofweek
    regression_df['day_of_month'] = regression_df.index.day
    regression_df['month'] = regression_df.index.month
    regression_df['year'] = regression_df.index.year
    regression_df['week_of_year'] = regression_df.index.isocalendar().week.astype(int)
    regression_df['is_month_end'] = regression_df.index.is_month_end.astype(int)
    regression_df['previous_day_revenue'] = regression_df['total_revenue'].shift(1).fillna(0)

    print("\n--- Training Short-Term Model (XGBoost) ---")
    X = regression_df.drop('total_revenue', axis=1)
    y = regression_df['total_revenue']

    short_term_model = XGBRegressor(n_estimators=500, learning_rate=0.01, random_state=42)
    short_term_model.fit(X, y)
    print("Short-Term Model (XGBoost) trained.")

    print("\n--- Training Long-Term Model (Prophet) ---")
    prophet_df = daily_df.reset_index().rename(columns={'sale_date': 'ds', 'total_revenue': 'y'})
    
    # AQUI ESTÁ A CORREÇÃO: Removemos o argumento 'daily_seasonality'
    prophet_model = Prophet() 
    
    prophet_model.add_country_holidays(country_name='BR')
    prophet_model.fit(prophet_df)
    print("Prophet model trained.")

    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    with open(SHORT_TERM_MODEL_PATH, 'wb') as f:
        pickle.dump(short_term_model, f)
    print(f"Short-Term Model saved to '{SHORT_TERM_MODEL_PATH}'")

    with open(LONG_TERM_MODEL_PATH, 'wb') as f:
        pickle.dump(prophet_model, f)
    print(f"Prophet Model saved to '{LONG_TERM_MODEL_PATH}'")

    print("\nTraining process completed successfully!")

except Exception as e:
    print(f"\nFATAL ERROR DURING TRAINING: {e}")
    sys.exit(1)