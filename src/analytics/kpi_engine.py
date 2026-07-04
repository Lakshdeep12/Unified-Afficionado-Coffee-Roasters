def calculate_total_revenue(df):
    return round(df['revenue'].sum(), 2)

def calculate_total_transactions(df):
    return df['transaction_id'].nunique()

def calculate_average_order_value(df):
    return round(df['revenue'].mean(), 2)

def get_peak_hour(df):
    return (
        df.groupby('hour')['transaction_id']
        .count()
        .idxmax()
    )

def get_best_day(df):
    return (
        df.groupby('day_name')['revenue']
        .sum()
        .idxmax()
    )