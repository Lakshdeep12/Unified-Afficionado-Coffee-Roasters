import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

from src.path_utils import resolve_dataset_path, resolve_raw_data_path

# Set page config first!
st.set_page_config(
    page_title="Afficionado Coffee Roasters Sales Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import local engines
from src.data_preprocessing import assign_time_bucket, run_preprocessing
from src.kpi_calculations import calculate_kpis, get_store_performance, get_hourly_trends, get_day_of_week_trends
from src.statistical_analysis import run_all_tests
from dashboard.components import inject_custom_css, render_kpi_card, render_line_chart, render_area_chart, render_bar_chart, render_heatmap, render_box_violin_plots, render_pie_donut, render_treemap, COLORS

# Inject custom premium stylesheet
inject_custom_css()

# Resolve the dataset path dynamically so the app works in local and deployed environments.
PROCESSED_DATA_PATH = resolve_dataset_path()
RAW_DATA_PATH = resolve_raw_data_path()
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "data_quality_report.md")

@st.cache_data
def load_data():
    if not os.path.exists(PROCESSED_DATA_PATH):
        if os.path.exists(RAW_DATA_PATH):
            st.info("Processed dataset missing; generating it from the raw source data...")
            run_preprocessing(RAW_DATA_PATH, PROCESSED_DATA_PATH, REPORT_PATH)
        else:
            st.error(f"Processed dataset not found at: {PROCESSED_DATA_PATH}")
            st.error(f"Raw data not found at: {RAW_DATA_PATH}")
            return pd.DataFrame()

    if not os.path.exists(PROCESSED_DATA_PATH):
        st.error(f"Processed dataset could not be generated at: {PROCESSED_DATA_PATH}")
        return pd.DataFrame()

    df = pd.read_csv(PROCESSED_DATA_PATH)
    # Ensure datetime parsing
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    return df

df_raw = load_data()

if df_raw.empty:
    st.warning("Please verify data exists. Dashboard cannot load.")
    st.stop()

# --- SIDEBAR HEADER & NAVIGATION (AT THE TOP) ---
st.sidebar.markdown("<div style='text-align: center; padding-bottom: 20px;'><h2 style='color:#D4A373; margin:0;'>☕ Afficionado</h2><p style='color:#94A3B8; margin:0; font-size:12px;'>Coffee Roasters Analytics</p></div>", unsafe_allow_html=True)

# Define page names with emojis
pages_dict = {
    "🏠 Home Dashboard": "Home Dashboard",
    "📈 Sales Trends": "Sales Trends",
    "⏰ Time Analysis": "Time Analysis",
    "📅 Day Analysis": "Day Analysis",
    "🏪 Store Comparison": "Store Comparison",
    "🧪 Statistical Analysis": "Statistical Analysis",
    "💡 Insights & Recommendations": "Insights & Recommendations"
}

selected_page_emoji = st.sidebar.radio(
    "Navigation Menu",
    list(pages_dict.keys())
)
page = pages_dict[selected_page_emoji]

st.sidebar.markdown("---")

# --- INTERACTIVE FILTERS EXPANDER (BELOW NAVIGATION) ---
with st.sidebar.expander("🛠️ Interactive Filters", expanded=True):
    # 1. Store Location
    locations = ["All"] + sorted(df_raw['store_location'].unique().tolist())
    selected_store = st.selectbox("Store Location", locations)

    # 2. Month Filter
    months_order = ['January', 'February', 'March', 'April', 'May', 'June']
    available_months = [m for m in months_order if m in df_raw['month'].unique()]
    selected_months = st.multiselect("Months", available_months, default=available_months)

    # 3. Day of Week Filter
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    selected_days = st.multiselect("Days of the Week", days_order, default=days_order)

    # 4. Hour Range Slider
    min_hour = int(df_raw['hour'].min())
    max_hour = int(df_raw['hour'].max())
    selected_hours = st.slider("Hours of Operation", min_hour, max_hour, (min_hour, max_hour))

    # 5. Product Category & Cascading Type
    categories = ["All"] + sorted(df_raw['product_category'].unique().tolist())
    selected_cat = st.selectbox("Product Category", categories)

    if selected_cat != "All":
        available_types = sorted(df_raw[df_raw['product_category'] == selected_cat]['product_type'].unique().tolist())
    else:
        available_types = sorted(df_raw['product_type'].unique().tolist())
    selected_types = st.multiselect("Product Types", available_types, default=[])

    # 6. Weekday vs Weekend filter
    day_type = st.radio("Day Type Filter", ["All Days", "Weekdays Only", "Weekends Only"])

    # 7. Revenue vs Quantity Toggle
    metric_choice = st.radio("Metric Selector", ["Revenue ($)", "Quantity Sold"])

# --- FILTER APPLICATION LOGIC ---
df_filtered = df_raw.copy()

# Apply store filter
if selected_store != "All":
    df_filtered = df_filtered[df_filtered['store_location'] == selected_store]

# Apply month filter
df_filtered = df_filtered[df_filtered['month'].isin(selected_months)]

# Apply day filter
df_filtered = df_filtered[df_filtered['day_of_week'].isin(selected_days)]

# Apply hour filter
df_filtered = df_filtered[(df_filtered['hour'] >= selected_hours[0]) & (df_filtered['hour'] <= selected_hours[1])]

# Apply category filter
if selected_cat != "All":
    df_filtered = df_filtered[df_filtered['product_category'] == selected_cat]

# Apply product type filter
if len(selected_types) > 0:
    df_filtered = df_filtered[df_filtered['product_type'].isin(selected_types)]

# Apply weekday/weekend filter
if day_type == "Weekdays Only":
    df_filtered = df_filtered[df_filtered['is_weekend'] == 0]
elif day_type == "Weekends Only":
    df_filtered = df_filtered[df_filtered['is_weekend'] == 1]

# Set the active metric column
metric_col = 'revenue' if metric_choice == "Revenue ($)" else 'transaction_qty'
metric_label = 'Revenue ($)' if metric_choice == "Revenue ($)" else 'Quantity Sold'
metric_format = "${:,.2f}" if metric_choice == "Revenue ($)" else "{:,.0f}"

st.sidebar.markdown("<div class='footer'>Afficionado Coffee Roasters © 2026<br>Academic Capstone Project</div>", unsafe_allow_html=True)

# ----------------- PAGE 1: HOME DASHBOARD -----------------
if page == "Home Dashboard":
    st.markdown("<h1 class='main-title'>Sales Trend & Time-Based Performance</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:16px;'>Executive Business Intelligence Dashboard for Afficionado Coffee Roasters (H1 2025)</p>", unsafe_allow_html=True)
    
    # Calculate KPIs
    kpis = calculate_kpis(df_filtered)
    
    # Render KPI Cards in columns
    c1, c2, c3, c4 = st.columns(4)
    render_kpi_card("Total Revenue", f"${kpis['total_revenue']:,.2f}", "H1 2025 Sales", c1)
    render_kpi_card("Transactions", f"{kpis['total_transactions']:,}", "Volume of Orders", c2)
    render_kpi_card("Quantity Sold", f"{kpis['total_quantity']:,}", "Individual Items", c3)
    render_kpi_card("Average Order Value", f"${kpis['average_order_value']:.2f}", "Avg Revenue per Order", c4)
    
    st.markdown("<div class='section-title'>Project Overview & Context</div>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""
        <div class='glass-card'>
            <h3 style='color:#D4A373; margin-top:0;'>Operational Challenges</h3>
            <p style='color:#E2E8F0; line-height:1.6;'>
                Afficionado Coffee Roasters operates a busy network of retail shops. Historically, staffing schedules and operating hours
                were determined by manager intuition, leading to severe resource imbalances:
            </p>
            <ul style='color:#E2E8F0; line-height:1.6;'>
                <li><b>Overstaffing</b> during mid-afternoon slumps, inflating overhead costs.</li>
                <li><b>Understaffing</b> during morning rush hours, causing long queues, slower service, and customer friction.</li>
                <li><b>Inconsistent Customer Experience</b> due to sudden demand swings.</li>
                <li><b>Inefficient inventory prep</b> resulting in waste or out-of-stock events for high-margin bakery items.</li>
            </ul>
            <p style='color:#E2E8F0; line-height:1.6;'>
                This analytical platform bridges the gap, providing empirical proof of <b>WHEN</b> customers purchase. By dissecting transaction patterns 
                across hours, days, stores, and product lines, it enables Afficionado's management to optimize their labor force, align store operations 
                with demand, and drive profit margins.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_right:
        st.markdown(f"""
        <div class='glass-card'>
            <h3 style='color:#D4A373; margin-top:0;'>Temporal Quick-Facts</h3>
            <table style='width:100%; border-collapse:collapse; color:#E2E8F0;'>
                <tr style='border-bottom:1px solid rgba(255,255,255,0.05);'><td style='padding:10px 0;'><b>Busiest Day</b></td><td style='text-align:right; color:#E9C46A;'>{kpis['best_day']}</td></tr>
                <tr style='border-bottom:1px solid rgba(255,255,255,0.05);'><td style='padding:10px 0;'><b>Slowest Day</b></td><td style='text-align:right; color:#E76F51;'>{kpis['worst_day']}</td></tr>
                <tr style='border-bottom:1px solid rgba(255,255,255,0.05);'><td style='padding:10px 0;'><b>Peak Hour</b></td><td style='text-align:right; color:#E9C46A;'>{kpis['peak_hour']}:00</td></tr>
                <tr style='border-bottom:1px solid rgba(255,255,255,0.05);'><td style='padding:10px 0;'><b>Slowest Hour</b></td><td style='text-align:right; color:#E76F51;'>{kpis['lowest_hour']}:00</td></tr>
            </table>
            <br>
            <p style='font-size:12px; color:#94A3B8; margin-top:10px;'>
                <i>*Based on currently applied sidebar filters. Adjust filters to update facts.</i>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div class='section-title'>Product Portfolio Matrix</div>", unsafe_allow_html=True)
    
    # Product Category breakdown
    cat_summary = (
        df_filtered.groupby('product_category')
        .agg(revenue=('revenue', 'sum'), quantity=('transaction_qty', 'sum'))
        .reset_index()
    )
    
    col_pie, col_tree = st.columns(2)
    with col_pie:
        fig_pie = render_pie_donut(cat_summary, 'product_category', metric_col, f"Share of Total {metric_label} by Category")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_tree:
        fig_tree = render_treemap(df_filtered, ['product_category', 'product_type'], metric_col, f"Detailed {metric_label} Hierarchy")
        st.plotly_chart(fig_tree, use_container_width=True)

# ----------------- PAGE 2: SALES TRENDS -----------------
elif page == "Sales Trends":
    st.markdown("<h1 class='main-title'>Sales Trend Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:16px;'>Examine sales progressions, growth trajectories, and moving averages throughout 2025.</p>", unsafe_allow_html=True)
    
    # 1. Daily Trend
    daily_sales = (
        df_filtered.groupby('transaction_date')
        .agg(
            metric_val=(metric_col, 'sum'),
            tx_count=('transaction_id', 'count')
        )
        .reset_index()
        .sort_values('transaction_date')
    )
    
    # Calculate 7-day Moving Average
    daily_sales['moving_avg'] = daily_sales['metric_val'].rolling(window=7, min_periods=1).mean()
    
    st.markdown("<div class='section-title'>Daily Performance & Moving Average</div>", unsafe_allow_html=True)
    
    # Custom Plotly with Line + Moving Average
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(
        x=daily_sales['transaction_date'],
        y=daily_sales['metric_val'],
        name="Daily Value",
        line=dict(color='rgba(212, 163, 115, 0.4)', width=1.5)
    ))
    fig_daily.add_trace(go.Scatter(
        x=daily_sales['transaction_date'],
        y=daily_sales['moving_avg'],
        name="7-Day Moving Avg",
        line=dict(color=COLORS['accent'], width=3)
    ))
    
    # Setup dark theme styling
    fig_daily.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Outfit, sans-serif", size=12, color=COLORS['text']),
        height=450,
        margin=dict(l=50, r=30, t=20, b=50),
        xaxis=dict(gridcolor=COLORS['grid'], showline=True, linecolor='#334155'),
        yaxis=dict(gridcolor=COLORS['grid'], showline=True, linecolor='#334155'),
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right", bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_daily, use_container_width=True)
    
    st.markdown("""
    <div class='glass-card' style='margin-top:10px;'>
        <p style='color:#E2E8F0; margin:0;'>
            <b>Business Interpretation:</b> The moving average line smooths out daily fluctuations (which are heavily driven by weekday/weekend schedules) 
            to reveal the underlying sales direction. Notice that sales show a steady baseline but experience cyclical weekend drops/increases, 
            which indicates differences in day-level demand scales.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Weekly and Monthly Aggregations
    col_w, col_m = st.columns(2)
    
    with col_w:
        # Weekly
        weekly_sales = (
            df_filtered.groupby('week_number')
            .agg(metric_val=(metric_col, 'sum'))
            .reset_index()
            .sort_values('week_number')
        )
        fig_week = render_area_chart(weekly_sales, 'week_number', 'metric_val', f"Weekly {metric_label} Progression", "Week Number", metric_label)
        st.plotly_chart(fig_week, use_container_width=True)
        
    with col_m:
        # Monthly
        monthly_sales = (
            df_filtered.groupby('month')
            .agg(metric_val=(metric_col, 'sum'))
            .reset_index()
        )
        # Order months
        monthly_sales['month'] = pd.Categorical(monthly_sales['month'], categories=months_order, ordered=True)
        monthly_sales = monthly_sales.sort_values('month')
        
        # Calculate month-over-month growth
        monthly_sales['mom_growth'] = monthly_sales['metric_val'].pct_change() * 100
        
        fig_month = render_bar_chart(monthly_sales, 'month', 'metric_val', f"Monthly {metric_label} Aggregation", "Month", metric_label)
        st.plotly_chart(fig_month, use_container_width=True)
        
    # Growth metric cards
    st.markdown("### Month-over-Month Growth (H1 2025)")
    cg1, cg2, cg3, cg4, cg5 = st.columns(5)
    
    for i, m in enumerate(months_order[1:]):  # Feb to Jun
        m_val = monthly_sales[monthly_sales['month'] == m]['metric_val'].values
        m_growth = monthly_sales[monthly_sales['month'] == m]['mom_growth'].values
        
        val_str = metric_format.format(m_val[0]) if len(m_val) > 0 else "N/A"
        growth_str = f"{m_growth[0]:+.1f}%" if len(m_growth) > 0 and not np.isnan(m_growth[0]) else "N/A"
        
        col_ref = [cg1, cg2, cg3, cg4, cg5][i]
        
        # Determine color of growth indicator
        if "%" in growth_str and "+" in growth_str:
            sub = f"<span style='color:{COLORS['cool_teal']}'>MoM: {growth_str}</span>"
        else:
            sub = f"<span style='color:{COLORS['warm_red']}'>MoM: {growth_str}</span>"
            
        render_kpi_card(f"{m}", val_str, sub, col_ref)

# ----------------- PAGE 3: TIME ANALYSIS -----------------
elif page == "Time Analysis":
    st.markdown("<h1 class='main-title'>Time-of-Day Demand Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:16px;'>Discover peak and off-peak hours to optimize barista staffing and inventory preparation.</p>", unsafe_allow_html=True)
    
    # 1. Hourly Trend Curve
    hourly_data = (
        df_filtered.groupby('hour')
        .agg(
            metric_val=(metric_col, 'sum'),
            tx_count=('transaction_id', 'count')
        )
        .reset_index()
    )
    
    col_curve, col_bucket = st.columns([2, 1])
    
    with col_curve:
        # We plot both the selected metric and the transaction count to show demand density
        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Scatter(
            x=hourly_data['hour'],
            y=hourly_data['metric_val'],
            name=metric_label,
            line=dict(color=COLORS['primary'], width=3),
            mode="lines+markers"
        ))
        apply_plotly_dark_template(fig_hourly, title=f"Hourly {metric_label} Curve", x_title="Hour of Day (24-Hour)", y_title=metric_label)
        # Force x-ticks for all hours
        fig_hourly.update_layout(xaxis=dict(tickmode='linear', tick0=6, dtick=1))
        st.plotly_chart(fig_hourly, use_container_width=True)
        
    with col_bucket:
        # Time bucket share
        bucket_data = (
            df_filtered.groupby('time_bucket')
            .agg(metric_val=(metric_col, 'sum'))
            .reset_index()
        )
        fig_bucket = render_pie_donut(bucket_data, 'time_bucket', 'metric_val', "Share by Operational Time Bucket")
        st.plotly_chart(fig_bucket, use_container_width=True)
        
    st.markdown("<div class='section-title'>The Five Operational Shifts</div>", unsafe_allow_html=True)
    
    # Split explanations
    st.markdown("""
    <div class='glass-card'>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>
            <div>
                <h4 style='color:#D4A373; margin-top:0;'>🌅 Morning Rush (06:00 - 11:59)</h4>
                <p style='color:#E2E8F0; font-size:13px; line-height:1.5; margin:0;'>
                    <b>Insights:</b> This is the undisputed peak period representing over 50% of daily transactions. Customers are buying quick morning coffees (Drip, Brewed Tea) and high-margin pastries.
                    <br><b>Staffing:</b> Maximize capacity. Baristas should be fully scheduled with zero administrative tasks.
                </p>
            </div>
            <div>
                <h4 style='color:#E9C46A; margin-top:0;'>☀️ Midday/Lunch (12:00 - 14:59)</h4>
                <p style='color:#E2E8F0; font-size:13px; line-height:1.5; margin:0;'>
                    <b>Insights:</b> A secondary, moderate peak representing lunchtime traffic. Orders shift slightly towards cold beverages and specialty roasts.
                    <br><b>Staffing:</b> Keep standard staffing levels. Utilize this period for inventory refills and food counter cleanup.
                </p>
            </div>
            <div>
                <h4 style='color:#F4A261; margin-top:0;'>🌇 Afternoon Slump (15:00 - 16:59)</h4>
                <p style='color:#E2E8F0; font-size:13px; line-height:1.5; margin:0;'>
                    <b>Insights:</b> A significant drop-off in transaction volumes. The "caffeine rush" subsides, and stores experience lowest daylight demand.
                    <br><b>Staffing:</b> Reduce staff. Transition baristas to restocking, cleaning, and preparation tasks.
                </p>
            </div>
            <div>
                <h4 style='color:#E76F51; margin-top:0;'>🌃 Evening / Late Hours</h4>
                <p style='color:#E2E8F0; font-size:13px; line-height:1.5; margin:0;'>
                    <b>Insights:</b> Demand tapers down significantly. Transactions drop to minimal levels after 19:00.
                    <br><b>Staffing:</b> Minimum closing crew. Prepare register reconciliations and shut down secondary espresso machinery.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- PAGE 4: DAY ANALYSIS -----------------
elif page == "Day Analysis":
    st.markdown("<h1 class='main-title'>Day-of-Week Performance</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:16px;'>Compare customer behaviors between individual weekdays, weekends, and overall schedules.</p>", unsafe_allow_html=True)
    
    # 1. Day of Week aggregate
    day_summary = (
        df_filtered.groupby('day_of_week')
        .agg(
            revenue=('revenue', 'sum'),
            transactions=('transaction_id', 'nunique'),
            quantity=('transaction_qty', 'sum')
        )
        .reindex(days_order)
        .dropna(subset=['revenue'])
        .reset_index()
    )
    
    col_day_val, col_day_tx = st.columns(2)
    with col_day_val:
        # Sum of metric by day
        fig_day_bar = render_bar_chart(day_summary, 'day_of_week', metric_col, f"Total {metric_label} by Day of Week", "Day", metric_label)
        st.plotly_chart(fig_day_bar, use_container_width=True)
        
    with col_day_tx:
        # Average revenue per order across days of week (box/violin style distribution)
        # We sample or use the whole df if size is okay. The whole df is 149k rows. Box/violin plots on 149k points can be slow, so we aggregate average order value per day
        day_avg = (
            df_filtered.groupby(['transaction_date', 'day_of_week'])['revenue']
            .mean()
            .reset_index()
        )
        fig_day_dist = render_box_violin_plots(day_avg, 'day_of_week', 'revenue', "Distribution of Daily Average Order Value ($)", "Day", "Avg Order Value ($)", chart_type='box')
        st.plotly_chart(fig_day_dist, use_container_width=True)
        
    # 2. Weekday vs Weekend Analysis
    st.markdown("<div class='section-title'>Weekday vs Weekend Comparison</div>", unsafe_allow_html=True)
    
    # Calculate daily averages for weekdays vs weekends
    df_daily_totals = (
        df_filtered.groupby(['transaction_date', 'is_weekend'])
        .agg(
            revenue=('revenue', 'sum'),
            transactions=('transaction_id', 'nunique'),
            quantity=('transaction_qty', 'sum')
        )
        .reset_index()
    )
    
    avg_comparison = (
        df_daily_totals.groupby('is_weekend')
        .agg(
            avg_daily_revenue=('revenue', 'mean'),
            avg_daily_transactions=('transactions', 'mean'),
            avg_daily_quantity=('quantity', 'mean')
        )
        .reset_index()
    )
    avg_comparison['Day Type'] = avg_comparison['is_weekend'].map({0: 'Weekday (Mon-Fri)', 1: 'Weekend (Sat-Sun)'})
    
    col_text, col_chart = st.columns([1, 1])
    
    with col_text:
        st.markdown("""
        <div class='glass-card' style='height: 100%;'>
            <h3 style='color:#D4A373; margin-top:0;'>Customer Behavior Insights</h3>
            <p style='color:#E2E8F0; line-height:1.6;'>
                Our analysis shows a clear separation between customer volumes on weekdays vs weekends:
            </p>
            <ul style='color:#E2E8F0; line-height:1.6;'>
                <li><b>Volume-Driven Differences:</b> Total daily revenue and transaction counts are higher on average during weekdays. This matches a commuter customer base that visits Afficionado during their work schedules.</li>
                <li><b>Order Size Consistency:</b> Interestingly, our statistical T-test shows <b>no significant difference</b> in the amount spent per transaction between weekdays and weekends ($4.69 vs $4.68). Customers do not order larger sizes or buy more items when they visit on weekends; they spend the same amount.</li>
                <li><b>Operational Strategy:</b> Labor allocation should be scheduled to handle higher overall volume (foot traffic) during weekdays, rather than preparing for larger orders on weekends.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_chart:
        metric_val_daily = 'avg_daily_revenue' if metric_col == 'revenue' else 'avg_daily_quantity'
        metric_label_daily = 'Average Daily Revenue ($)' if metric_col == 'revenue' else 'Average Daily Quantity Sold'
        fig_week_comp = render_bar_chart(avg_comparison, 'Day Type', metric_val_daily, f"Weekday vs Weekend: {metric_label_daily}", "Day Type", metric_label_daily)
        st.plotly_chart(fig_week_comp, use_container_width=True)

# ----------------- PAGE 5: STORE COMPARISON -----------------
elif page == "Store Comparison":
    st.markdown("<h1 class='main-title'>Store-Level Comparisons</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:16px;'>Compare customer behaviors, transaction volumes, and hourly demand peaks across different physical locations.</p>", unsafe_allow_html=True)
    
    # Store performance summary
    store_perf = get_store_performance(df_filtered)
    # Calculate AOV per store
    store_perf['aov'] = store_perf['revenue'] / store_perf['transactions']
    
    # Render Store KPIs in Columns
    c_s1, c_s2, c_s3 = st.columns(3)
    for i, row in store_perf.iterrows():
        col_ref = [c_s1, c_s2, c_s3][i]
        render_kpi_card(
            row['store_location'],
            f"${row['revenue']:,.2f}",
            f"{row['transactions']:,} transactions | AOV: ${row['aov']:.2f}",
            col_ref
        )
        
    st.markdown("<div class='section-title'>Store Heatmaps & Hourly Profiles</div>", unsafe_allow_html=True)
    
    # Store X Hour Pivot Table
    store_hour_pivot = df_filtered.pivot_table(
        values=metric_col,
        index='store_location',
        columns='hour',
        aggfunc='sum'
    ).fillna(0)
    
    fig_store_heatmap = render_heatmap(store_hour_pivot, f"Store Location × Hour Demand Density Map ({metric_label})", "Hour of Day", "Store Location")
    st.plotly_chart(fig_store_heatmap, use_container_width=True)
    
    # Clustered Bar Chart: Product Categories by Store
    st.markdown("<div class='section-title'>Product Mix per Store Location</div>", unsafe_allow_html=True)
    store_cat = df_filtered.groupby(['store_location', 'product_category'])[metric_col].sum().reset_index()
    fig_store_cat = px.bar(
        store_cat,
        x='product_category',
        y=metric_col,
        color='store_location',
        barmode='group',
        color_discrete_sequence=[COLORS['primary'], COLORS['cool_teal'], COLORS['accent']]
    )
    apply_plotly_dark_template(fig_store_cat, title="Product Category Breakdown by Store Location", x_title="Product Category", y_title=metric_label)
    st.plotly_chart(fig_store_cat, use_container_width=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h3 style='color:#D4A373; margin-top:0;'>Location-Specific Customer Insights</h3>
        <ul style='color:#E2E8F0; line-height:1.6;'>
            <li><b>Lower Manhattan (Financial District Hub):</b> Drives the highest transaction size (Average Order Value of $4.81). Order density is highly concentrated in the morning work hour (08:00 - 10:00). High demand for premium Coffee Beans and Espresso.</li>
            <li><b>Hell's Kitchen (Residential/Commuter Hub):</b> The busiest overall store by volume (over 50,000 transactions). Demand is steady and persistent from 07:00 through 14:00, representing a mix of local residents and workers.</li>
            <li><b>Astoria (Neighborhood Leisure Hub):</b> Features lower average order values ($4.59) but a strong and steady flow of Tea, Bakery, and loose tea items. The weekend drop-off is less severe here compared to the financial center, suggesting a strong residential weekend client base.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ----------------- PAGE 6: STATISTICAL ANALYSIS -----------------
elif page == "Statistical Analysis":
    st.markdown("<h1 class='main-title'>Statistical Analysis & Hypotheses Testing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:16px;'>Rigorous statistical validation of business assumptions on Afficionado's transaction data.</p>", unsafe_allow_html=True)
    
    # Run tests on filtered dataframe
    with st.spinner("Running statistical calculations..."):
        test_results = run_all_tests(df_filtered)
        
    st.markdown("<div class='section-title'>1. One-Way ANOVA: Store Location vs. Revenue</div>", unsafe_allow_html=True)
    
    anova_store = test_results['anova_store']
    c_a1, c_a2, c_a3 = st.columns(3)
    c_a1.metric("F-Statistic", f"{anova_store['statistic']:.4f}")
    c_a2.metric("P-value", f"{anova_store['p_value']:.4e}")
    c_a3.metric("Decision", anova_store['decision'])
    
    st.markdown(f"""
    <div class='glass-card'>
        <p><b>Objective:</b> {anova_store['objective']}</p>
        <p><b>Hypotheses:</b><br>&nbsp;&nbsp;&nbsp;&nbsp;<b>Null (H0):</b> {anova_store['null_hypothesis']}<br>&nbsp;&nbsp;&nbsp;&nbsp;<b>Alternative (H1):</b> {anova_store['alt_hypothesis']}</p>
        <p><b>Conclusion:</b> {anova_store['conclusion']}</p>
        <p><b>Business Interpretation:</b> {anova_store['interpretation']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>2. Independent Welch's T-Test: Weekday vs. Weekend Revenue</div>", unsafe_allow_html=True)
    
    ttest_w = test_results['ttest_weekend']
    c_t1, c_t2, c_t3 = st.columns(3)
    c_t1.metric("T-Statistic", f"{ttest_w['statistic']:.4f}")
    c_t2.metric("P-value", f"{ttest_w['p_value']:.4f}")
    c_t3.metric("Decision", ttest_w['decision'])
    
    st.markdown(f"""
    <div class='glass-card'>
        <p><b>Objective:</b> {ttest_w['objective']}</p>
        <p><b>Hypotheses:</b><br>&nbsp;&nbsp;&nbsp;&nbsp;<b>Null (H0):</b> {ttest_w['null_hypothesis']}<br>&nbsp;&nbsp;&nbsp;&nbsp;<b>Alternative (H1):</b> {ttest_w['alt_hypothesis']}</p>
        <p><b>Conclusion:</b> {ttest_w['conclusion']}</p>
        <p><b>Business Interpretation:</b> {ttest_w['interpretation']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>3. Chi-Square Test of Independence: Store Location vs. Product Category</div>", unsafe_allow_html=True)
    
    chi = test_results['chisquare_store_category']
    c_c1, c_c2, c_c3 = st.columns(3)
    c_c1.metric("Chi-Square Statistic", f"{chi['statistic']:.2f}")
    c_c2.metric("P-value", f"{chi['p_value']:.4e}")
    c_c3.metric("Decision", chi['decision'])
    
    st.markdown(f"""
    <div class='glass-card'>
        <p><b>Objective:</b> {chi['objective']}</p>
        <p><b>Hypotheses:</b><br>&nbsp;&nbsp;&nbsp;&nbsp;<b>Null (H0):</b> {chi['null_hypothesis']}<br>&nbsp;&nbsp;&nbsp;&nbsp;<b>Alternative (H1):</b> {chi['alt_hypothesis']}</p>
        <p><b>Conclusion:</b> {chi['conclusion']}</p>
        <p><b>Business Interpretation:</b> {chi['interpretation']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>4. Correlation Matrix (Numerical Features)</div>", unsafe_allow_html=True)
    
    corr = test_results['correlation']
    
    col_corr_table, col_corr_text = st.columns([1, 1])
    with col_corr_table:
        st.dataframe(corr['correlation_matrix'].style.background_gradient(cmap='copper_r', axis=None))
    with col_corr_text:
        st.markdown(f"""
        <div class='glass-card'>
            <h4 style='color:#D4A373; margin-top:0;'>Correlation Insights</h4>
            <p style='color:#E2E8F0; line-height:1.6;'>
                {corr['interpretation']}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ----------------- PAGE 7: INSIGHTS & RECOMMENDATIONS -----------------
elif page == "Insights & Recommendations":
    st.markdown("<h1 class='main-title'>Evidence-Based Business Recommendations</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:16px;'>Data-driven, actionable recommendations to improve staffing efficiency, operational schedules, and customer satisfaction.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h2 style='color:#D4A373; margin-top:0;'>1. Staffing & Scheduling Optimization</h2>
        <h4 style='color:#E9C46A;'>The Challenge: High labor costs during slow hours and long wait lines during peak hours.</h4>
        <p style='color:#E2E8F0; line-height:1.6;'>
            <b>Evidence:</b> 54.8% of all transactions occur during the <i>Morning (06:00 - 11:59)</i> window, peaking specifically between 08:00 and 10:00. Conversely, the <i>Afternoon Slump (15:00 - 16:59)</i> sees a drop-off of over 70% in transaction volume.
        </p>
        <p style='color:#E2E8F0; line-height:1.6;'>
            <b>Actionable Recommendations:</b>
        </p>
        <ul style='color:#E2E8F0; line-height:1.6;'>
            <li><b>Implement Tiered Staffing:</b> Transition to a demand-based schedule. Schedule peak staffing (3-4 baristas) from 07:00 to 11:00. Reduce to a skeleton crew (1-2 baristas) starting at 14:00.</li>
            <li><b>Differentiate Store Roles:</b> Assign a dedicated "Order Runner" during the morning rush (08:00 - 10:00) who focuses entirely on handing off food and drip coffee, keeping the register and espresso baristas working at maximum throughput.</li>
        </ul>
    </div>
    
    <div class='glass-card'>
        <h2 style='color:#D4A373; margin-top:0;'>2. Adjusting Operating Hours</h2>
        <h4 style='color:#E9C46A;'>The Challenge: Inefficient utility and labor spend in late evenings.</h4>
        <p style='color:#E2E8F0; line-height:1.6;'>
            <b>Evidence:</b> Less than 2% of total store revenue is generated after 19:00 across all locations. Running full store operations past this time generates negative net operating margins.
        </p>
        <p style='color:#E2E8F0; line-height:1.6;'>
            <b>Actionable Recommendations:</b>
        </p>
        <ul style='color:#E2E8F0; line-height:1.6;'>
            <li><b>Standardize Early Closing:</b> Move closing hours from 20:00 or 21:00 to 19:00 at all locations. This will reduce operational costs (electricity, cleaning labor) with minimal impact on top-line revenue.</li>
            <li><b>Early Morning Opening (Financial District):</b> For the Lower Manhattan store, open 30 minutes earlier (06:30 instead of 07:00) to capture early commuter traffic.</li>
        </ul>
    </div>
    
    <div class='glass-card'>
        <h2 style='color:#D4A373; margin-top:0;'>3. Targeted Promotions & Inventory Planning</h2>
        <h4 style='color:#E9C46A;'>The Challenge: Perishable food waste and stagnant afternoon sales.</h4>
        <p style='color:#E2E8F0; line-height:1.6;'>
            <b>Evidence:</b> Bakery items represent 15% of transactions but have high profit margins. The correlation between unit price and revenue is strong (0.6855), indicating that premium coffee beans and higher-priced items drive revenue.
        </p>
        <p style='color:#E2E8F0; line-height:1.6;'>
            <b>Actionable Recommendations:</b>
        </p>
        <ul style='color:#E2E8F0; line-height:1.6;'>
            <li><b>The "Afternoon Pick-Me-Up" Promo:</b> Introduce a bundled deal (e.g. coffee + pastry for a discount) between 14:00 and 16:00 to incentivize visits during the afternoon slump.</li>
            <li><b>Inventory Prep Schedules:</b> Align bakery baking times. Ensure fresh pastries are fully stocked by 07:00. Do not bake fresh items after 13:00 to avoid end-of-day markdown write-offs.</li>
            <li><b>Neighborhood Customization:</b> Capitalize on the Chi-Square results. Allocate more retail shelf space for Gourmet Coffee Beans at the Lower Manhattan store, and expand the hot chocolate/specialty tea selection at the Astoria location.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
