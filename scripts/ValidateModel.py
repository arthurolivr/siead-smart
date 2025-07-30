import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import argparse

from repositories.VendaRepository import fetch_all_sales


def validate(db_name: str):
    print(f"--- Starting validation for database: {db_name.upper()} ---")

    df = fetch_all_sales(db_name)
    print("Data fetched successfully.")

    df['sale_date'] = pd.to_datetime(df['data_venda'])
    daily_df = (
        df.groupby('sale_date')['valor_total']
          .sum()
          .to_frame(name='total_revenue')
    )
    
    regression_df = daily_df.copy()
    assert isinstance(regression_df.index, pd.DatetimeIndex)

    idx_series = regression_df.index.to_series()
    regression_df['day_of_week']       = idx_series.dt.dayofweek
    regression_df['day_of_month']      = idx_series.dt.day
    regression_df['month']             = idx_series.dt.month
    regression_df['year']              = idx_series.dt.year
    regression_df['week_of_year']      = idx_series.dt.isocalendar().week.astype(int)
    regression_df['is_month_end']      = idx_series.dt.is_month_end.astype(int)
    regression_df['previous_day_revenue'] = regression_df['total_revenue'].shift(1).fillna(0)

    days_to_test = 30
    train_data = regression_df.iloc[:-days_to_test]
    test_data  = regression_df.iloc[-days_to_test:]

    print(f"\nUsing {len(train_data)} days to train the model.")
    print(f"Using {len(test_data)} days to validate the prediction.")

    X_train = train_data.drop('total_revenue', axis=1)
    y_train = train_data['total_revenue']
    X_test  = test_data.drop('total_revenue', axis=1)
    y_real  = test_data['total_revenue']

    print("\nTraining a temporary optimized XGBoost model...")
    temp_model = XGBRegressor(
        n_estimators=1000,
        learning_rate=0.01,
        early_stopping_rounds=5,
        random_state=42
    )
    temp_model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_real)],
        verbose=False
    )

    print("Making predictions for the test period...")
    y_predicted = temp_model.predict(X_test).clip(min=0)

    print("\n--- REFINED MODEL EVALUATION ---")
    validation_df = pd.DataFrame(
        {'Real': y_real, 'Predicted': y_predicted},
        index=y_real.index
    )
    mae = mean_absolute_error(y_real, y_predicted)
    print(f"\nThe model's Mean Absolute Error (MAE) is: R$ {mae:,.2f}")
    print("\nGenerating comparison plot...")
    plt.figure(figsize=(15, 7))
    plt.plot(validation_df.index, validation_df['Real'], marker='o', linestyle='-', label='Actual Revenue')
    plt.plot(validation_df.index, validation_df['Predicted'], marker='x', linestyle='--', label='Predicted Revenue')
    plt.title('Optimized Model Validation: Actual vs. Predicted Revenue (Last 30 Days)')
    plt.xlabel('Date')
    plt.ylabel('Revenue (R$)')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate prediction models for a specific database."
    )
    parser.add_argument(
        "--db",
        type=str,
        required=True,
        choices=['famart', 'ipb'],
        help="The database name to validate on."
    )
    args = parser.parse_args()
    validate(args.db)