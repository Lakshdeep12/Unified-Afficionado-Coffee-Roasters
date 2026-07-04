import pandas as pd
import numpy as np

def calculate_kpis(df):
    """
    Calculate core high-level KPIs for the given dataframe.
    """
    if df.empty:
        return {
            'total_revenue': 0.0,
            'total_transactions': 0,
            'total_quantity': 0,
            'average_order_value': 0.0,
            'best_day': "N/A",
            'worst_day': "N/A",
            'peak_hour': "N/A",
            'lowest_hour': "N/A"
        }
        
    total_rev = df['revenue'].sum()
    total_tx = df['transaction_id'].nunique()
    total_qty = df['transaction_qty'].sum()
    aov = total_rev / total_tx if total_tx > 0 else 0.0
    
    # Day-of-week performance
    day_rev = df.groupby('day_of_week')['revenue'].sum()
    best_day = day_rev.idxmax() if not day_rev.empty else "N/A"
    worst_day = day_rev.idxmin() if not day_rev.empty else "N/A"
    
    # Hourly performance
    hour_tx = df.groupby('hour')['transaction_id'].count()
    peak_hour = hour_tx.idxmax() if not hour_tx.empty else "N/A"
    lowest_hour = hour_tx.idxmin() if not hour_tx.empty else "N/A"
    
    return {
        'total_revenue': round(total_rev, 2),
        'total_transactions': total_tx,
        'total_quantity': total_qty,
        'average_order_value': round(aov, 2),
        'best_day': best_day,
        'worst_day': worst_day,
        'peak_hour': peak_hour,
        'lowest_hour': lowest_hour
    }

def get_store_performance(df):
    """
    Group performance metrics by store location.
    """
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby('store_location')
        .agg(
            revenue=('revenue', 'sum'),
            transactions=('transaction_id', 'nunique'),
            quantity=('transaction_qty', 'sum')
        )
        .reset_index()
    )

def get_hourly_trends(df):
    """
    Group performance metrics by hour.
    """
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby('hour')
        .agg(
            revenue=('revenue', 'sum'),
            transactions=('transaction_id', 'nunique'),
            quantity=('transaction_qty', 'sum')
        )
        .reset_index()
    )

def get_day_of_week_trends(df):
    """
    Group performance metrics by day of week.
    """
    if df.empty:
        return pd.DataFrame()
    
    # Define categorical order for days of the week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    summary = (
        df.groupby('day_of_week')
        .agg(
            revenue=('revenue', 'sum'),
            transactions=('transaction_id', 'nunique'),
            quantity=('transaction_qty', 'sum')
        )
        .reindex(day_order)
        .reset_index()
    )
    
    # Drop rows that are NaN (in case some days aren't in the filtered df)
    return summary.dropna(subset=['revenue'])
