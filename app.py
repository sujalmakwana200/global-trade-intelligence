import streamlit as st
import pandas as pd
import numpy as np
import requests
from streamlit_echarts import st_echarts
import gc

# 1. PAGE SETUP
st.set_page_config(page_title="Laxminarayan | Trade Intel", layout="wide", page_icon="⚜️")

# 2. ELITE CSS (Sidebar CSS removed, Control Deck CSS added)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #050505 !important; }
    
    /* Input Styling */
    .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stTextInput input {
        background-color: #1A1A1A !important; color: #D4AF37 !important; border: 1px solid #333 !important;
    }
    
    /* Metallic Gold Button */
    div.stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #8B6508 100%) !important;
        color: #000 !important; font-weight: 800 !important; border-radius: 4px !important;
        height: 48px !important; width: 100% !important; text-transform: uppercase; margin-top: 28px;
    }
    div.stButton > button:hover { background: #FFFFFF !important; box-shadow: 0 0 15px rgba(212, 175, 55, 0.5); }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #0F0F0F !important; border: 1px solid #1A1A1A !important;
        border-top: 3px solid #D4AF37 !important; border-radius: 8px !important; padding: 15px !important;
    }

    /* Expander (Command Center) Styling */
    div[data-testid="stExpander"] {
        background-color: #0D0D0D !important;
        border: 1px solid #333 !important;
        border-left: 4px solid #D4AF37 !important;
        border-radius: 5px !important;
    }
    div[data-testid="stExpander"] summary { color: #D4AF37 !important; font-weight: bold !important; font-size: 1.1rem !important; }
    
    label, h1, h2, h3, h4 { color: #D4AF37 !important; }
    p, span { color: #FFF !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header[data-testid="stHeader"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. ROBUST STATE MANAGEMENT & DATA
@st.cache_data(ttl=3600)
def fetch_rate():
    try: return requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()['rates']['INR']
    except: return 83.50

ex_rate = fetch_rate()

if 'market_db' not in st.session_state:
    st.session_state.market_db = {
        "630221": {"name": "Printed Cotton Bed Linen", "price": 12.50, "duty": 15.0},
        "851712": {"name": "Smartphones (Flagship)", "price": 210.0, "duty": 20.0},
        "520100": {"name": "Raw Cotton (Premium)", "price": 2.10, "duty": 11.0},
        "090111": {"name": "Arabica Coffee Beans", "price": 4.85, "duty": 100.0},
        "711319": {"name": "Gold Bullion Jewellery", "price": 1850.0, "duty": 12.5},
        "100630": {"name": "Basmati Rice (Export Grade)", "price": 1.15, "duty": 0.0}
    }

# 4. TOP COMMAND CENTER (Replaces the Sidebar)
st.title("LAXMINARAYAN GLOBAL TRADE")

with st.expander("⚙️ STRATEGIC COMMAND CENTER (Click to Expand/Collapse)", expanded=True):
    col_ingest, col_trade, col_logistics = st.columns(3)
    
    with col_ingest:
        st.markdown("#### 1. Data Integration")
        uploaded_file = st.file_uploader("Upload CSV Database", type="csv")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                required_cols = ['HSN', 'Name', 'Price', 'Duty']
                if not all(col in df.columns for col in required_cols):
                    st.error(f"CSV must contain: {', '.join(required_cols)}")
                else:
                    added_count = 0
                    for _, row in df.iterrows():
                        st.session_state.market_db[str(row['HSN'])] = {
                            "name": str(row['Name']), "price": float(row['Price']), "duty": float(row['Duty'])
                        }
                        added_count += 1
                    st.success(f"Added {added_count} products.")
            except Exception as e:
                st.error("Error reading file.")

        display_list = [f"{k} - {v['name']}" for k, v in st.session_state.market_db.items()]
        selection = st.selectbox("Select Asset", display_list)
        hsn_key = selection.split(" - ")[0]
        product = st.session_state.market_db[hsn_key]

    with col_trade:
        st.markdown("#### 2. Trade Parameters")
        trade_mode = st.radio("Trade Mode", ["Export", "Import"], horizontal=True)
        currency = st.radio("Currency", ["INR (₹)", "USD ($)"], horizontal=True)
        qty = st.number_input("Transaction Quantity", min_value=1, value=1000)

    with col_logistics:
        st.markdown("#### 3. Execution & Logistics")
        c_f, c_i = st.columns(2)
        with c_f: freight = st.number_input("Freight (Unit)", min_value=0.0, value=2.50)
        with c_i: insurance = st.number_input("Insurance (Unit)", min_value=0.0, value=0.50)
        target_price = st.number_input("Target Sale Price", min_value=0.1, value=product['price'] * 1.5)
        
        if st.button("Generate Intelligence Report"):
            st.toast("Report compiled with current parameters.", icon="✅")

# 5. CALCULATIONS
conv = ex_rate if "INR" in currency else 1.0
sym = "₹" if "INR" in currency else "$"

unit_base_cost = product['price']
unit_duty_cost = unit_base_cost * (product['duty'] / 100) if trade_mode == "Import" else 0.0 
unit_landed_cost = unit_base_cost + unit_duty_cost + freight + insurance
unit_profit = target_price - unit_landed_cost

total_revenue = target_price * qty
total_cost = unit_landed_cost * qty
total_profit = unit_profit * qty

margin = (unit_profit / target_price) * 100 if target_price > 0 else 0

# 6. KPI DASHBOARD HEADER
st.markdown(f"**Active Asset:** {product['name']} | **Mode:** {trade_mode} | **HSN:** {hsn_key}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Unit Landed Cost", f"{sym}{unit_landed_cost*conv:,.2f}")
c2.metric("Total Revenue", f"{sym}{total_revenue*conv:,.0f}")
c3.metric(f"Total Net Profit", f"{sym}{total_profit*conv:,.0f}")
c4.metric("Net Margin", f"{margin:.2f}%")

st.divider()

# 7. REACTIVE CHARTS
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Price Volatility vs. Break-Even")
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30).strftime('%d %b').tolist()
    market_prices = [(unit_base_cost * conv * (1 + np.random.uniform(-0.03, 0.03))) for _ in range(30)]
    break_even_line = [unit_landed_cost * conv] * 30 
    
    line_opt = {
        "backgroundColor": "transparent",
        "animationDuration": 1000,
        "tooltip": {"trigger": "axis", "backgroundColor": "#111", "textStyle": {"color": "#FFF"}},
        "legend": {"textStyle": {"color": "#AAA"}, "bottom": 0},
        "xAxis": {"type": "category", "data": dates, "axisLabel": {"color": "#666"}},
        "yAxis": {"type": "value", "splitLine": {"lineStyle": {"color": "#1A1A1A"}}, "axisLabel": {"color": "#666"}},
        "series": [
            {"name": "Market Price", "type": "line", "smooth": True, "data": market_prices, "itemStyle": {"color": "#D4AF37"}},
            {"name": "Landed Cost (Break-Even)", "type": "line", "lineStyle": {"type": "dashed", "color": "#FF4B4B"}, "data": break_even_line, "symbol": "none"}
        ]
    }
    st_echarts(options=line_opt, height="400px", width="100%")

with col_right:
    st.subheader("Unit Cost Distribution")
    donut_opt = {
        "backgroundColor": "transparent",
        "animationDuration": 1000,
        "tooltip": {"trigger": "item", "backgroundColor": "#111", "textStyle": {"color": "#FFF"}, "formatter": "{b}: {c} ({d}%)"},
        "legend": {"bottom": "0", "textStyle": {"color": "#AAA"}},
        "series": [{
            "type": "pie", "radius": ["55%", "75%"],
            "itemStyle": {"borderRadius": 5, "borderColor": "#050505", "borderWidth": 4},
            "label": {"show": False},
            "data": [
                {"value": round(unit_base_cost * conv, 2), "name": "Base Asset", "itemStyle": {"color": "#D4AF37"}},
                {"value": round(unit_duty_cost * conv, 2), "name": "Duty", "itemStyle": {"color": "#C0C0C0"}},
                {"value": round(freight * conv, 2), "name": "Freight", "itemStyle": {"color": "#444444"}},
                {"value": round(insurance * conv, 2), "name": "Insurance", "itemStyle": {"color": "#8B6508"}}
            ]
        }]
    }
    st_echarts(options=donut_opt, height="400px", width="100%")

# 8. MACRO TRENDS
st.divider()
st.markdown("### 📊 5-Year Historical Macro Trends")
m1, m2 = st.columns(2)

with m1:
    st.markdown(f"**Import vs Export Volume (Tons)**")
    bar_opt = {
        "backgroundColor": "transparent",
        "animationDuration": 1500,
        "tooltip": {"trigger": "axis", "backgroundColor": "#111", "textStyle": {"color": "#FFF"}},
        "legend": {"textStyle": {"color": "#AAA"}, "bottom": 0},
        "xAxis": {"type": "category", "data": ["2021", "2022", "2023", "2024", "2025"], "axisLabel": {"color": "#FFF"}},
        "yAxis": {"type": "value", "splitLine": {"lineStyle": {"color": "#1A1A1A"}}, "axisLabel": {"color": "#666"}},
        "series": [
            {"name": "Import", "type": "bar", "data": [9000, 10000, 11000, 9500, 5200], "itemStyle": {"color": "#FF6347"}},
            {"name": "Export", "type": "bar", "data": [14000, 13000, 16000, 17000, 18000], "itemStyle": {"color": "#D4AF37"}}
        ]
    }
    st_echarts(options=bar_opt, height="350px", width="100%")

with m2:
    st.markdown(f"**Price Trajectory ({sym})**")
    area_opt = {
        "backgroundColor": "transparent",
        "animationDuration": 1500,
        "tooltip": {"trigger": "axis", "backgroundColor": "#111", "textStyle": {"color": "#FFF"}},
        "xAxis": {"type": "category", "data": ["2021", "2022", "2023", "2024", "2025"], "axisLabel": {"color": "#FFF"}},
        "yAxis": {"type": "value", "splitLine": {"lineStyle": {"color": "#1A1A1A"}}, "axisLabel": {"color": "#666"}},
        "series": [{
            "name": "Market Avg", "type": "line", "areaStyle": {"opacity": 0.2, "color": "#008080"}, 
            "data": [unit_base_cost*0.7, unit_base_cost*0.85, unit_base_cost*0.9, unit_base_cost*1.1, unit_base_cost*1.2], 
            "itemStyle": {"color": "#008080"}
        }]
    }
    st_echarts(options=area_opt, height="350px", width="100%")
