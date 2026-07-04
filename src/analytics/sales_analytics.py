def get_daily_sales(df):

    return (
        df.groupby('transaction_date')['revenue']
        .sum()
        .reset_index()
    )

def get_weekly_sales(df):

    return (
        df.groupby('day_name')['revenue']
        .sum()
        .reset_index()
    )

def get_monthly_sales(df):

    return (
        df.groupby('month')['revenue']
        .sum()
        .reset_index()
    )