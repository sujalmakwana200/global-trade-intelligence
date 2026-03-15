import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="Laxminarayan Trade Intel", layout="wide")

def get_exchange_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url).json()
        return response['rates']['INR']
    except:
        return 89.0

# --- GLOBAL HSN DATABASE ---
MOCK_DB = {
    "520100": {"name": "Raw Cotton (Not carded/combed)", "price_usd": 2.10, "duty": 11.0},
    "630221": {"name": "Printed Cotton Bed Linen", "price_usd": 12.50, "duty": 15.0},
    "851712": {"name": "Smartphones", "price_usd": 210.00, "duty": 20.0},
    "090111": {"name": "Coffee Beans (Not roasted)", "price_usd": 4.50, "duty": 100.0},
    "847130": {"name": "Laptops & Portable Computers", "price_usd": 650.00, "duty": 0.0},
    "870899": {"name": "Automotive Parts & Accessories", "price_usd": 45.00, "duty": 15.0}
}

# --- HEADER ---
st.title("🌍 Laxminarayan Global Trade Intelligence")
st.markdown("Analyze profitability and macro trends in your preferred currency.")

# --- FINAL POLISH: GLOBAL CURRENCY TOGGLE ---
currency_mode = st.radio("Display Currency:", ["INR (₹)", "USD ($)"], horizontal=True)
symbol = "₹" if "INR" in currency_mode else "$"
exchange_rate = get_exchange_rate()

# Conversion Multiplier
# If user wants USD, we divide INR values by the exchange rate
conv = 1.0 if "INR" in currency_mode else (1.0 / exchange_rate)

st.markdown("---")

# --- SIDEBAR: DATABASE & UPLOADER ---
st.sidebar.header("1. Data Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Custom Database (CSV)", type=["csv"])

if uploaded_file:
    try:
        custom_df = pd.read_csv(uploaded_file)
        for _, row in custom_df.iterrows():
            MOCK_DB[str(row['HSN'])] = {"name": row['Name'], "price_usd": float(row['Price_USD']), "duty": float(row['Duty'])}
        st.sidebar.success(f"Loaded {len(custom_df)} custom products!")
    except:
        st.sidebar.error("Format: HSN, Name, Price_USD, Duty")

search_options = ["Custom Product (Manual)"] + [f"{c} - {d['name']}" for c, d in MOCK_DB.items()]
selected_item = st.sidebar.selectbox("Find Product", search_options)

if selected_item != "Custom Product (Manual)":
    hsn_code = selected_item.split(" - ")[0]
    data = MOCK_DB[hsn_code]
    product_name, base_cost_inr, customs_duty_pct = data['name'], data['price_usd'] * exchange_rate, data['duty']
    st.sidebar.info(f"Auto-Fetched: {product_name}")
else:
    product_name = st.sidebar.text_input("Product Name", "Custom Item")
    base_cost_inr = st.sidebar.number_input("Base Cost (INR)", 500.0)
    customs_duty_pct = st.sidebar.number_input("Duty (%)", 11.0)

quantity = st.sidebar.number_input("Quantity", 1, value=1000)

# --- SIDEBAR: LOGISTICS & TRADE ---
st.sidebar.header("2. Logistics & Trade")
freight_inr, insurance_inr = st.sidebar.number_input("Freight (INR)", 50.0), st.sidebar.number_input("Insurance (INR)", 15.0)
trade_type = st.sidebar.radio("Trade Mode", ["Export", "Import"])

if trade_type == "Export":
    sell_price_usd = st.sidebar.number_input("Target Price (USD)", 15.0)
    rev_inr = sell_price_usd * exchange_rate
else:
    sell_price_inr = st.sidebar.number_input("Target Price (INR)", 1200.0)
    rev_inr = sell_price_inr

# --- CALCULATIONS (All in INR internally) ---
duty_val_inr = base_cost_inr * (customs_duty_pct / 100)
unit_cost_inr = base_cost_inr + freight_inr + insurance_inr + duty_val_inr
unit_profit_inr = rev_inr - unit_cost_inr
total_profit_inr = unit_profit_inr * quantity
margin = (unit_profit_inr / rev_inr) * 100 if rev_inr > 0 else 0

# --- METRICS ROW (Converted) ---
st.subheader(f"Dashboard: {product_name}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Exchange Rate", f"₹{exchange_rate:.2f}")
m2.metric(f"Unit Cost ({symbol})", f"{symbol}{unit_cost_inr * conv:,.2f}")
m3.metric(f"Unit Revenue ({symbol})", f"{symbol}{rev_inr * conv:,.2f}")
m4.metric("Net Margin", f"{margin:.1f}%", f"{symbol}{total_profit_inr * conv:,.0f} Total")

st.markdown("---")

# --- MIDDLE ROW: MICRO TRENDS & DONUT ---
c_line, c_donut = st.columns([2, 1])

with c_line:
    st.subheader(f"30-Day Volatility ({symbol})")
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
    # Generate mock data and convert it
    vols = [(base_cost_inr * (1 + np.random.uniform(-0.05, 0.05))) * conv for _ in range(30)]
    st.line_chart(pd.DataFrame({f"Price ({symbol})": vols}, index=dates))

with c_donut:
    st.subheader("Cost Distribution")
    fig_donut = go.Figure(data=[go.Pie(
        labels=["Base", "Freight", "Insurance", "Duty"],
        values=[base_cost_inr * conv, freight_inr * conv, insurance_inr * conv, duty_val_inr * conv],
        hole=.65,
        marker=dict(colors=["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"]),
        textinfo='percent',
        textposition='outside'
    )])
    fig_donut.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=300)
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# --- BOTTOM ROW: MACRO ANALYTICS ---
st.subheader("📊 5-Year Historical Macro Trends")
years = [str(y) for y in range(2021, 2026)]
c_bar, c_area = st.columns(2)

with c_bar:
    # Volume is quantity-based, so no conversion needed
    df_vol = pd.DataFrame({"Year": years * 2, "Tons": [np.random.randint(5000, 15000) for _ in range(5)] + [np.random.randint(8000, 20000) for _ in range(5)], "Type": ["Import"]*5 + ["Export"]*5})
    st.plotly_chart(px.bar(df_vol, x="Year", y="Tons", color="Type", barmode="group", title="Import vs Export Vol", color_discrete_map={"Import":"#F06543","Export":"#313638"}), use_container_width=True)

with c_area:
    # Price Trajectory needs conversion
    df_price = pd.DataFrame({"Year": years, f"Avg Price ({symbol})": [(base_cost_inr * (1 + (int(y)-2025)*0.06)) * conv for y in years]})
    st.plotly_chart(px.area(df_price, x="Year", y=f"Avg Price ({symbol})", title=f"Price Trajectory ({symbol})", color_discrete_sequence=["#2A9D8F"]), use_container_width=True)

# --- CSV EXPORT ---
st.download_button("Download Report (CSV)", df_vol.to_csv().encode('utf-8'), f"{product_name}_report.csv", "text/csv")
