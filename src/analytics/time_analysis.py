def get_hourly_sales(df):

    return (
        df.groupby('hour')['revenue']
        .sum()
        .reset_index()
    )

def get_hourly_transactions(df):

    return (
        df.groupby('hour')['transaction_id']
        .count()
        .reset_index()
    )

def get_time_bucket_sales(df):

    return (
        df.groupby('time_bucket')['revenue']
        .sum()
        .reset_index()
    )