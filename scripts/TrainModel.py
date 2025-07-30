import pandas as pd
from xgboost import XGBRegressor
from prophet import Prophet
import pickle
import argparse
import os

from repositories.VendaRepository import fetch_all_sales
from config import get_model_paths

def train(db_name: str):
    print(f"--- Starting training process for database: {db_name.upper()} ---")
    df = fetch_all_sales(db_name)
    print("Data fetched successfully. Preparing features...")

    df['sale_date'] = pd.to_datetime(df['data_venda'])
    daily_df = df.groupby('sale_date')['valor_total']\
                .sum()\
                .to_frame(name='total_revenue')
    
    regression_df = daily_df.copy()
    assert isinstance(regression_df.index, pd.DatetimeIndex)

    idx_series = regression_df.index.to_series()
    regression_df['day_of_week']     = idx_series.dt.dayofweek
    regression_df['day_of_month']    = idx_series.dt.day
    regression_df['month']           = idx_series.dt.month
    regression_df['year']            = idx_series.dt.year
    regression_df['week_of_year']    = idx_series.dt.isocalendar().week.astype(int)
    regression_df['is_month_end']    = idx_series.dt.is_month_end.astype(int)
    regression_df['previous_day_revenue'] = regression_df['total_revenue'].shift(1).fillna(0)

    print("\n--- Training Short-Term Model (XGBoost) ---")
    X = regression_df.drop('total_revenue', axis=1)
    y = regression_df['total_revenue']

    short_term_model = XGBRegressor(n_estimators=500, learning_rate=0.01, random_state=42)
    short_term_model.fit(X, y)
    print("Short-Term Model (XGBoost) trained.")

    print("\n--- Training Long-Term Model (Prophet) ---")
    prophet_df = daily_df.reset_index().rename(columns={'sale_date': 'ds', 'total_revenue': 'y'})
    prophet_model = Prophet()
    prophet_model.add_country_holidays(country_name='BR')
    prophet_model.fit(prophet_df)
    print("Prophet model trained.")

    model_paths = get_model_paths(db_name)
    os.makedirs(os.path.dirname(model_paths['short_term']), exist_ok=True)

    with open(model_paths['short_term'], 'wb') as f:
        pickle.dump(short_term_model, f)
    print(f"Short-Term Model saved to '{model_paths['short_term']}'")

    with open(model_paths['long_term'], 'wb') as f:
        pickle.dump(prophet_model, f)
    print(f"Prophet Model saved to '{model_paths['long_term']}'")

    print(f"\nTraining process for {db_name.upper()} completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train prediction models for a specific database."
    )
    parser.add_argument(
        "--db",
        type=str,
        required=True,
        choices=['famart', 'ipb'],
        help="The database name to train on."
    )
    args = parser.parse_args()
    train(args.db)