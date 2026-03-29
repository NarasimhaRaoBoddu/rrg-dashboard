import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from fyers_apiv3 import fyersModel

# 1. యాప్ సెట్టింగ్స్
st.set_page_config(page_title="Live Trading Chart", page_icon="📈", layout="wide")
st.title("📊 Fyers Live Candlestick Chart")

# ==========================================
# 2. FYERS CREDENTIALS
# ==========================================
CLIENT_ID = "QHIBBNGEQE-100"      # ఉదా: "QHIBBNGEQE-100"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCcHlQUlhBTUpsRXduZERZczBjWGJmT0MwRXN4X3ZDaHVfdThPQnlVcFJFbTdJNU5tQXdiZjdVSFFNdVM1cTBzU1hsZkpzVWd0V0R3eENsemEtSzJKRnBrV19LbE5KX1lobVNCbTJWZEItdERPTzJ4TT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiIxOTk3NWUyOGVlZjQ0YWM4YzE3NGE3MjQyYjgzNjlhMWM4YzE0ZGVkMWRiMjFkYTNlOGI4M2U0MSIsImlzRGRwaUVuYWJsZWQiOiJZIiwiaXNNdGZFbmFibGVkIjoiWSIsImZ5X2lkIjoiWU4xMTU5MSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzc0ODMwNjAwLCJpYXQiOjE3NzQ3Nzc0MzEsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc3NDc3NzQzMSwic3ViIjoiYWNjZXNzX3Rva2VuIn0.cwiru3JptArYldschrXS0QuskKKvpMMjxVj94wkTmgI"    # మీ పెద్ద మాస్టర్ టోకెన్

# Fyers లాగిన్
try:
    fyers = fyersModel.FyersModel(client_id=CLIENT_ID, is_async=False, token=ACCESS_TOKEN, log_path="")
except Exception as e:
    st.error(f"Fyers Login Error: {e}")

# 3. యూజర్ సెలెక్షన్ కోసం (సెక్టార్లు & టైమ్‌ఫ్రేమ్)
symbols = {
    'NIFTY 50': 'NSE:NIFTY50-INDEX', 'BANK NIFTY': 'NSE:NIFTYBANK-INDEX', 
    'FIN NIFTY': 'NSE:FINNIFTY-INDEX', 'RELIANCE': 'NSE:RELIANCE-EQ',
    'HDFC BANK': 'NSE:HDFCBANK-EQ'
}

resolutions = {'1 Min': '1', '5 Min': '5', '15 Min': '15', '1 Hour': '60', '1 Day': '1D'}

col1, col2, col3 = st.columns([2, 2, 1])
sel_name = col1.selectbox("ఇండెక్స్ / స్టాక్ సెలెక్ట్ చేయండి:", list(symbols.keys()))
sel_res = col2.selectbox("టైమ్‌ఫ్రేమ్:", list(resolutions.keys()))

sym = symbols[sel_name]
res = resolutions[sel_res]

# రీఫ్రెష్ బటన్ 
if col3.button("🔄 లైవ్ రీఫ్రెష్"):
    st.cache_data.clear() # పాత డేటాని క్లియర్ చేసి కొత్తది లాగుతుంది

# 4. Fyers నుండి చార్ట్ డేటా లాగే ఫంక్షన్
@st.cache_data(ttl=60) # ప్రతి 1 నిమిషానికి ఆటోమెటిక్ గా డేటా రిఫ్రెష్ అవుతుంది
def get_chart_data(symbol, resolution):
    end_date = datetime.date.today()
    
    # టైమ్‌ఫ్రేమ్ ని బట్టి ఎన్ని రోజుల డేటా లాగాలో డిసైడ్ చేస్తాం
    if resolution == '1D':
        start_date = end_date - datetime.timedelta(days=100) # డైలీ చార్ట్ కి 100 రోజులు
    else:
        start_date = end_date - datetime.timedelta(days=4)   # ఇంట్రాడే కి 4 రోజులు చాలు
        
    payload = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": "1",
        "range_from": start_date.strftime("%Y-%m-%d"),
        "range_to": end_date.strftime("%Y-%m-%d"),
        "cont_flag": "1"
    }
    
    response = fyers.history(data=payload)
    if response.get('s') == 'ok':
        df = pd.DataFrame(response['candles'], columns=['epoch', 'Open', 'High', 'Low', 'Close', 'Volume'])
        # టైమ్ ని ఇండియన్ టైమ్ (IST) లోకి మార్చడం
        df['Date'] = pd.to_datetime(df['epoch'], unit='s')
        df['Date'] = df['Date'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        return df
    else:
        st.error(f"డేటా రాలేదు: {response}")
        return pd.DataFrame()

# 5. చార్ట్ గీయడం (Plotly)
with st.spinner("చార్ట్ లోడ్ అవుతోంది... ⚡"):
    df = get_chart_data(sym, res)

if not df.empty:
    # Plotly Candlestick డిజైన్
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=sel_name,
        increasing_line_color='lime',  # గ్రీన్ క్యాండిల్ కలర్
        decreasing_line_color='red'    # రెడ్ క్యాండిల్ కలర్
    )])
    
    # చార్ట్ లేఅవుట్ (అందంగా డార్క్ థీమ్ లో కనిపించడానికి)
    fig.update_layout(
        title=f"<b>{sel_name}</b> - {sel_res} Live Chart",
        yaxis_title="Price",
        xaxis_title="Time",
        template="plotly_dark", # డార్క్ మోడ్
        height=650,             # చార్ట్ సైజు
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    # కింద అనవసరమైన స్లైడర్ ని తీసేయడం (క్లీన్ గా ఉండటానికి)
    fig.update_xaxes(rangeslider_visible=False)
    
    # స్ట్రీమ్‌లిట్ లో చార్ట్ ని ప్రదర్శించడం
    st.plotly_chart(fig, use_container_width=True)

    # ప్రస్తుత లైవ్ ప్రైస్ కింద చూపించడం
    st.success(f"📌 **{sel_name}** Current LTP: **{df['Close'].iloc[-1]:.2f}**")
