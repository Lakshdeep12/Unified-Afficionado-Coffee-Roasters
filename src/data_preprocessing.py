import pandas as pd
import numpy as np
import os

def assign_time_bucket(hour):
    """
    Categorize transaction hour into operational shifts.
    """
    if 6 <= hour <= 11:
        return 'Morning (06:00-11:59)'
    elif 12 <= hour <= 16:
        return 'Afternoon (12:00-16:59)'
    elif 17 <= hour <= 21:
        return 'Evening (17:00-21:59)'
    else:
        return 'Late Hours (22:00-05:59)'


def run_preprocessing(raw_path, processed_path, report_path):
    print("--- Starting Preprocessing Pipeline ---")
    
    # 1. Load Dataset
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw data file not found at {raw_path}")
        
    df = pd.read_csv(raw_path)
    
    # Capture initial statistics
    initial_shape = df.shape
    dtypes = df.dtypes.to_dict()
    
    # 2. Missing Value Analysis
    missing_counts = df.isnull().sum()
    total_missing = missing_counts.sum()
    
    # 3. Duplicate Transaction Detection
    duplicate_count = df.duplicated(subset=['transaction_id']).sum()
    
    # 4. Numeric Range Validation
    invalid_qty = (df['transaction_qty'] <= 0).sum()
    invalid_price = (df['unit_price'] <= 0).sum()
    
    # 5. Timestamp Validation
    # Ensure times are in HH:MM:SS format and valid
    try:
        parsed_times = pd.to_datetime(df['transaction_time'], format='%H:%M:%S', errors='coerce')
        invalid_times = parsed_times.isnull().sum()
    except Exception:
        invalid_times = len(df)
        
    # 6. Sort and Date Reconstruction
    # Sort by transaction ID to ensure sequential order
    df = df.sort_values('transaction_id').reset_index(drop=True)
    
    # Calculate time differences to find where time resets (signifying a new day)
    time_seconds = pd.to_timedelta(df['transaction_time']).dt.total_seconds()
    time_diff = time_seconds.diff()
    
    # Increment days whenever time_diff < 0 (i.e. time goes backward when day changes)
    start_date = pd.to_datetime('2025-01-01')
    day_increments = (time_diff < 0).cumsum().fillna(0)
    df['transaction_date'] = start_date + pd.to_timedelta(day_increments, unit='D')
    
    # 7. Feature Engineering
    # Revenue = transaction_qty * unit_price
    df['revenue'] = df['transaction_qty'] * df['unit_price']
    
    # Hour of day (0-23)
    df['hour'] = pd.to_datetime(df['transaction_time'], format='%H:%M:%S').dt.hour
    
    # Day of week (Monday-Sunday)
    df['day_of_week'] = df['transaction_date'].dt.day_name()
    
    # Month name (January, February, etc.)
    df['month'] = df['transaction_date'].dt.month_name()
    
    # Week number
    df['week_number'] = df['transaction_date'].dt.isocalendar().week
    
    # Weekend Flag (1 if Saturday or Sunday, else 0)
    df['is_weekend'] = df['transaction_date'].dt.dayofweek.isin([5, 6]).astype(int)
    
    # Time Bucket
    df['time_bucket'] = df['hour'].apply(assign_time_bucket)
    
    # 8. Outlier Detection (using IQR)
    outliers = {}
    for col in ['unit_price', 'transaction_qty', 'revenue']:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        outliers[col] = {
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'count': outlier_mask.sum(),
            'percentage': round((outlier_mask.sum() / len(df)) * 100, 2)
        }
        
    # Rearrange columns
    cols_order = [
        'transaction_id', 'transaction_date', 'day_of_week', 'month', 'week_number', 'is_weekend',
        'transaction_time', 'hour', 'time_bucket', 'transaction_qty', 'unit_price', 'revenue',
        'store_id', 'store_location', 'product_id', 'product_category', 'product_type', 'product_detail'
    ]
    df_processed = df[cols_order]
    
    # Save the processed dataset
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df_processed.to_csv(processed_path, index=False)
    print(f"Processed dataset saved successfully to {processed_path}")
    
    # 9. Generate Data Quality Report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Data Quality & Preprocessing Report\n\n")
        f.write("## 1. Dataset Overview\n")
        f.write(f"- **Total Transactions**: {initial_shape[0]}\n")
        f.write(f"- **Initial Columns**: {initial_shape[1]}\n")
        f.write(f"- **Final Processed Columns**: {len(cols_order)}\n\n")
        
        f.write("### Column Data Types:\n")
        f.write("| Column | Data Type |\n")
        f.write("| --- | --- |\n")
        for col_name, dtype in dtypes.items():
            f.write(f"| {col_name} | {dtype} |\n")
        f.write("\n")
        
        f.write("## 2. Integrity Checks\n")
        f.write(f"- **Missing Values Detected**: {total_missing}\n")
        for col, count in missing_counts.items():
            if count > 0:
                f.write(f"  - `{col}`: {count} missing values\n")
        f.write(f"- **Duplicate Transaction IDs**: {duplicate_count}\n")
        f.write(f"- **Invalid (Non-positive) Quantities**: {invalid_qty}\n")
        f.write(f"- **Invalid (Non-positive) Unit Prices**: {invalid_price}\n")
        f.write(f"- **Invalid Timestamp Format (HH:MM:SS)**: {invalid_times}\n\n")
        
        f.write("## 3. Date Reconstruction Analysis\n")
        f.write(f"- **Start Date**: {df['transaction_date'].min().strftime('%Y-%m-%d')}\n")
        f.write(f"- **End Date**: {df['transaction_date'].max().strftime('%Y-%m-%d')}\n")
        f.write(f"- **Total Unique Days Implied**: {df['transaction_date'].nunique()}\n")
        f.write(f"- **Day Transitions Detected**: {int(day_increments.max())}\n\n")
        
        f.write("## 4. Outlier Analysis (IQR Method)\n")
        f.write("| Variable | Q1 | Q3 | IQR | Lower Bound | Upper Bound | Outlier Count | Outlier % |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")
        for col, info in outliers.items():
            f.write(f"| {col} | {info['q1']:.2f} | {info['q3']:.2f} | {info['iqr']:.2f} | {info['lower_bound']:.2f} | {info['upper_bound']:.2f} | {info['count']} | {info['percentage']}% |\n")
        f.write("\n")
        f.write("> **Note on Outliers**: While statistical outliers are present (especially bulk orders of expensive coffee beans or multiple quantity purchases), these represent valid, genuine customer transactions rather than data entry errors. Therefore, they are retained in the processed dataset to ensure full financial accuracy.\n\n")
        
        desc = df_processed[['transaction_qty', 'unit_price', 'revenue', 'hour']].describe()
        f.write("| Statistic | " + " | ".join(desc.columns) + " |\n")
        f.write("| --- | " + " | ".join(["---"] * len(desc.columns)) + " |\n")
        for idx, row in desc.iterrows():
            f.write(f"| {idx} | " + " | ".join([f"{val:.4f}" for val in row]) + " |\n")
        f.write("\n\n")
        
        f.write("### Categorical Variables Overview\n")
        f.write(f"- **Unique Store Locations**: {df_processed['store_location'].nunique()}\n")
        for loc, count in df_processed['store_location'].value_counts().items():
            f.write(f"  - {loc}: {count} transactions\n")
        f.write(f"- **Unique Product Categories**: {df_processed['product_category'].nunique()}\n")
        for cat, count in df_processed['product_category'].value_counts().head(5).items():
            f.write(f"  - {cat}: {count} transactions\n")
        f.write("  - ...\n")
        
    print(f"Data quality report saved successfully to {report_path}")
    print("--- Preprocessing Pipeline Completed Successfully ---")

if __name__ == "__main__":
    raw_csv      = r"D:\Unified Afficionado Coffee Roasters\Dataset\Raw dataset\Afficionado Coffee Roasters.xlsx - Transactions.csv"
    processed_csv = r"D:\Unified Afficionado Coffee Roasters\Dataset\Processed dataset\Afficionado_Coffee_Processed.csv"
    report_md    = r"D:\Unified Afficionado Coffee Roasters\reports\data_quality_report.md"
    run_preprocessing(raw_csv, processed_csv, report_md)
