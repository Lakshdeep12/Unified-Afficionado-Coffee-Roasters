def get_store_revenue(df):

    return (
        df.groupby('store_location')['revenue']
        .sum()
        .reset_index()
    )

def get_store_transactions(df):

    return (
        df.groupby('store_location')['transaction_id']
        .count()
        .reset_index()
    )

def get_store_hourly_heatmap(df):

    return (
        df.pivot_table(
            values='revenue',
            index='store_location',
            columns='hour',
            aggfunc='sum'
        )
    )