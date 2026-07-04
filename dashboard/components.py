import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Theme Colors
COLORS = {
    'primary': '#D4A373',      # Warm Copper / Latte
    'secondary': '#895737',    # Coffee Brown
    'dark': '#1F1A17',         # Espresso Black
    'light': '#F4EAE1',        # Milk Cream
    'accent': '#E9C46A',       # Gold
    'cool_teal': '#2A9D8F',    # Mint Tea Accent
    'warm_coral': '#F4A261',   # Orange Accent
    'warm_red': '#E76F51',     # Sunset Red
    'background': '#0E1117',   # App BG
    'card_bg': 'rgba(30, 34, 42, 0.6)', # Glassmorphism Card BG
    'grid': '#2D3139',         # Grid Line Color
    'text': '#E2E8F0',         # Main Text
    'text_muted': '#94A3B8'    # Muted Text
}

def inject_custom_css():
    """
    Injects custom CSS to style the Streamlit app with premium glassmorphism aesthetics,
    custom fonts, and interactive micro-animations.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    
    /* Global font overwrite */
    html, body, [class*="css"], .stMarkdown, p, div, label {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Background override */
    .stApp {
        background-color: #0E1117;
        background-image: radial-gradient(circle at 10% 20%, rgba(74, 59, 50, 0.15) 0%, rgba(14, 17, 23, 1) 90.2%);
        background-attachment: fixed;
    }
    
    /* Glassmorphism KPI cards */
    .kpi-container {
        background: rgba(30, 34, 42, 0.5);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(212, 163, 115, 0.15);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    
    .kpi-container:hover {
        transform: translateY(-5px);
        border-color: rgba(212, 163, 115, 0.4);
        box-shadow: 0 12px 40px 0 rgba(212, 163, 115, 0.1);
    }
    
    .kpi-title {
        color: #94A3B8;
        font-size: 14px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        color: #D4A373;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .kpi-subtitle {
        color: #E9C46A;
        font-size: 12px;
        font-weight: 400;
    }
    
    /* Styled headers */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    .main-title {
        color: #D4A373;
        background: linear-gradient(135deg, #D4A373 0%, #E9C46A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 40px;
        margin-bottom: 5px;
        font-weight: 700;
        text-shadow: 0px 4px 20px rgba(212, 163, 115, 0.15);
    }
    
    .section-title {
        color: #E2E8F0;
        border-bottom: 2px solid rgba(212, 163, 115, 0.2);
        padding-bottom: 8px;
        margin-top: 25px;
        margin-bottom: 20px;
        font-size: 24px;
    }
    
    /* Metric Card Glow Accent */
    div[data-testid="stMetricValue"] {
        color: #D4A373 !important;
        font-weight: 700 !important;
    }
    
    /* Custom Sidebar styling */
    /* Custom Sidebar styling */
    div[data-testid="stSidebar"] {
        background-color: #0B0E14 !important;
        border-right: 1px solid rgba(212, 163, 115, 0.1) !important;
    }
    
    /* Custom Navigation Radio Button Styling */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] {
        background: rgba(30, 34, 42, 0.2) !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    /* General label transitions */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label {
        color: #94A3B8 !important;
        transition: background-color 0.2s ease !important;
        padding: 6px 10px !important;
        border-radius: 6px !important;
    }
    
    /* Hover state background */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background-color: rgba(212, 163, 115, 0.08) !important;
        color: #D4A373 !important;
    }
    
    /* Target the selected option label using :has */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
        background-color: rgba(212, 163, 115, 0.15) !important;
        color: #D4A373 !important;
    }
    
    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(30, 34, 42, 0.3);
        padding: 5px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 6px;
        color: #94A3B8;
        font-size: 14px;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
        padding: 0 16px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #D4A373;
        background-color: rgba(212, 163, 115, 0.08);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(212, 163, 115, 0.15) !important;
        color: #D4A373 !important;
        font-weight: 600 !important;
    }
    
    /* Custom containers */
    .glass-card {
        background: rgba(30, 34, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        color: #64748B;
        font-size: 13px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def render_kpi_card(title, value, subtitle="", col=None):
    """
    Renders a styled KPI card with glassmorphism effects.
    """
    html_content = f"""
    <div class="kpi-container">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """
    if col:
        return col.markdown(html_content, unsafe_allow_html=True)
    return st.markdown(html_content, unsafe_allow_html=True)

def apply_plotly_dark_template(fig, height=450, show_legend=True, title="", x_title="", y_title=""):
    """
    Applies a sleek custom dark template to a Plotly figure.
    """
    fig.update_layout(
        title={
            'text': f"<b>{title}</b>",
            'y': 0.95,
            'x': 0.02,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': {'family': 'Outfit, sans-serif', 'size': 18, 'color': '#E2E8F0'}
        },
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(family="Outfit, sans-serif", size=12, color=COLORS['text']),
        height=height,
        margin=dict(l=50, r=30, t=65, b=50),
        xaxis=dict(
            title=f"<b>{x_title}</b>",
            gridcolor=COLORS['grid'],
            showline=True,
            linecolor='#334155',
            linewidth=1,
            title_font=dict(size=13, color=COLORS['text_muted']),
            tickfont=dict(color=COLORS['text_muted'])
        ),
        yaxis=dict(
            title=f"<b>{y_title}</b>",
            gridcolor=COLORS['grid'],
            showline=True,
            linecolor='#334155',
            linewidth=1,
            title_font=dict(size=13, color=COLORS['text_muted']),
            tickfont=dict(color=COLORS['text_muted'])
        ),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=COLORS['text_muted']),
            bgcolor="rgba(0,0,0,0)"
        ),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family="Outfit, sans-serif",
            font_color="#E2E8F0",
            bordercolor="rgba(212, 163, 115, 0.3)"
        )
    )
    return fig

def render_line_chart(df, x_col, y_col, title, x_title, y_title, color_col=None, show_legend=True, mode="lines"):
    """
    Renders an elegant line chart using Plotly.
    """
    if color_col:
        fig = px.line(df, x=x_col, y=y_col, color=color_col, color_discrete_sequence=[COLORS['primary'], COLORS['cool_teal'], COLORS['warm_coral'], COLORS['accent'], COLORS['warm_red']])
    else:
        fig = px.line(df, x=x_col, y=y_col, color_discrete_sequence=[COLORS['primary']])
        
    if mode == "lines+markers":
        fig.update_traces(mode="lines+markers", marker=dict(size=6, line=dict(width=1, color='#1E293B')))
        
    fig.update_traces(line=dict(width=2.5))
    apply_plotly_dark_template(fig, title=title, x_title=x_title, y_title=y_title, show_legend=show_legend)
    return fig

def render_area_chart(df, x_col, y_col, title, x_title, y_title):
    """
    Renders a premium area chart using Plotly.
    """
    fig = px.area(df, x=x_col, y=y_col, color_discrete_sequence=[COLORS['primary']])
    fig.update_traces(
        line=dict(width=2, color=COLORS['primary']),
        fillcolor='rgba(212, 163, 115, 0.15)'
    )
    apply_plotly_dark_template(fig, title=title, x_title=x_title, y_title=y_title, show_legend=False)
    return fig

def render_bar_chart(df, x_col, y_col, title, x_title, y_title, color_col=None, show_legend=False, orientation='v'):
    """
    Renders an elegant bar chart.
    """
    if color_col:
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, 
                     color_discrete_sequence=[COLORS['primary'], COLORS['cool_teal'], COLORS['warm_coral'], COLORS['accent'], COLORS['warm_red']],
                     orientation=orientation)
    else:
        # Check if x_col or y_col has specific day order or store order to apply color
        color_seq = [COLORS['primary']] * len(df)
        fig = px.bar(df, x=x_col, y=y_col, color_discrete_sequence=[COLORS['primary']], orientation=orientation)
        fig.update_traces(marker_color=COLORS['primary'], marker_line_color='rgba(0,0,0,0)', opacity=0.85)
        
    apply_plotly_dark_template(fig, title=title, x_title=x_title, y_title=y_title, show_legend=show_legend)
    return fig

def render_heatmap(pivot_df, title, x_title, y_title):
    """
    Renders a custom styled heatmap.
    """
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale=[
            [0.0, '#111827'],      # Dark Gray
            [0.2, '#1E293B'],      # Dark Slate
            [0.5, '#5C3D2E'],      # Espresso
            [0.8, '#D4A373'],      # Copper
            [1.0, '#E9C46A']       # Gold
        ],
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> at <b>%{x}:00</b><br>Value: %{z:,.2f}<extra></extra>"
    ))
    
    apply_plotly_dark_template(fig, title=title, x_title=x_title, y_title=y_title, show_legend=False)
    fig.update_layout(margin=dict(l=100, r=30, t=65, b=50))
    return fig

def render_box_violin_plots(df, category_col, value_col, title, x_title, y_title, chart_type='box'):
    """
    Renders styled Box or Violin plots for distributions.
    """
    if chart_type == 'box':
        fig = px.box(df, x=category_col, y=value_col, color=category_col,
                     color_discrete_sequence=[COLORS['primary'], COLORS['cool_teal'], COLORS['warm_coral'], COLORS['accent'], COLORS['warm_red']])
    else:
        fig = px.violin(df, x=category_col, y=value_col, color=category_col, box=True, points="outliers",
                        color_discrete_sequence=[COLORS['primary'], COLORS['cool_teal'], COLORS['warm_coral'], COLORS['accent'], COLORS['warm_red']])
                        
    apply_plotly_dark_template(fig, title=title, x_title=x_title, y_title=y_title, show_legend=False)
    return fig

def render_pie_donut(df, names_col, values_col, title, is_donut=True):
    """
    Renders an elegant Pie or Donut chart.
    """
    hole_val = 0.4 if is_donut else 0.0
    fig = px.pie(df, names=names_col, values=values_col, hole=hole_val,
                 color_discrete_sequence=[COLORS['primary'], COLORS['cool_teal'], COLORS['warm_coral'], COLORS['accent'], COLORS['warm_red'], COLORS['secondary']])
                 
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#0E1117', width=2))
    )
    
    apply_plotly_dark_template(fig, title=title, show_legend=True)
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

def render_treemap(df, path_cols, values_col, title):
    """
    Renders a Treemap.
    """
    fig = px.treemap(df, path=path_cols, values=values_col,
                     color_discrete_sequence=[COLORS['primary'], COLORS['cool_teal'], COLORS['warm_coral'], COLORS['accent'], COLORS['secondary']])
    apply_plotly_dark_template(fig, title=title, show_legend=False)
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig
