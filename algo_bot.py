import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from fyers_apiv3 import fyersModel

# ==========================================
# 1. APP SETTINGS & FYERS LOGIN
# ==========================================
st.set_page_config(page_title="Ultimate Live Terminal", page_icon="⚡", layout="wide")
st.title("⚡ Ultimate 7989 Live Trading Terminal")
st.markdown("RRG Rotation | Live Charts | Auto-Bot Execution - Direct Fyers API")

# మీ డీటెయిల్స్ ఇక్కడ పేస్ట్ చేయండి
CLIENT_ID = "QHIBBNGEQE-100"      
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCcHlQUlhBTUpsRXduZERZczBjWGJmT0MwRXN4X3ZDaHVfdThPQnlVcFJFbTdJNU5tQXdiZjdVSFFNdVM1cTBzU1hsZkpzVWd0V0R3eENsemEtSzJKRnBrV19LbE5KX1lobVNCbTJWZEItdERPTzJ4TT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiIxOTk3NWUyOGVlZjQ0YWM4YzE3NGE3MjQyYjgzNjlhMWM4YzE0ZGVkMWRiMjFkYTNlOGI4M2U0MSIsImlzRGRwaUVuYWJsZWQiOiJZIiwiaXNNdGZFbmFibGVkIjoiWSIsImZ5X2lkIjoiWU4xMTU5MSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzc0ODMwNjAwLCJpYXQiOjE3NzQ3Nzc0MzEsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc3NDc3NzQzMSwic3ViIjoiYWNjZXNzX3Rva2VuIn0.cwiru3JptArYldschrXS0QuskKKvpMMjxVj94wkTmgI"    

try:
    fyers = fyersModel.FyersModel(client_id=CLIENT_ID, is_async=False, token=ACCESS_TOKEN, log_path="")
except Exception as e:
    st.error(f"Fyers Login Error: {e}")

# ==========================================
# 2. PRO ALGO BOT CLASS (మెదడు)
# ==========================================
class ProAlgoBot:
    def __init__(self, fyers_client, symbol, qty, sl_points, tp_points):
        self.fyers = fyers_client
        self.symbol = symbol
        self.qty = qty
        self.sl_points = sl_points
        self.tp_points = tp_points

    def execute_market_order(self, side_text):
        side = 1 if side_text == "BUY" else -1
        order_data = {
            "symbol": self.symbol, "qty": self.qty, "type": 2, "side": side,
            "productType": "INTRADAY", "limitPrice": 0, "stopPrice": 0,
            "validity": "DAY", "disclosedQty": 0, "offlineOrder": False
        }
        # నిజంగా Fyers లో ఆర్డర్ వెళ్లాలంటే ఈ కింద ఉన్న 3 లైన్స్ కామెంట్స్ (#) తీసేయండి
        res = self.fyers.place_order(data=order_data)
        if res.get('s') == 'ok': return True
        return False
        
        st.toast(f"✅ (LIVE TEST) {side_text} ఆర్డర్ ఎగ్జిక్యూట్ అయ్యింది! సింబల్: {self.symbol}")
        return True

# ==========================================
# 3. MEGA TERMINAL TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["📊 1. RRG డాష్‌బోర్డ్", "📈 2. లైవ్ చార్ట్స్", "🤖 3. ప్రో ఆటో-బోట్"])

# ------------------------------------------
# TAB 1: RRG DASHBOARD
# ------------------------------------------
with tab1:
    st.header("నిఫ్టీ సెక్టార్ల రొటేషన్ (Live RRG)")
    sectors = {
        'NIFTY 50': 'NSE:NIFTY50-INDEX', 'BANK': 'NSE:NIFTYBANK-INDEX', 
        'FINSRV': 'NSE:FINNIFTY-INDEX', 'IT': 'NSE:NIFTYIT-INDEX', 
        'AUTO': 'NSE:NIFTYAUTO-INDEX', 'METAL': 'NSE:NIFTYMETAL-INDEX', 
        'FMCG': 'NSE:NIFTYFMCG-INDEX', 'PHARMA': 'NSE:NIFTYPHARMA-INDEX', 
        'ENERGY': 'NSE:NIFTYENERGY-INDEX', 'REALTY': 'NSE:NIFTYREALTY-INDEX', 
        'MEDIA': 'NSE:NIFTYMEDIA-INDEX', 'INFRA': 'NSE:NIFTYINFRA-INDEX', 
        'PSE': 'NSE:NIFTYPSE-INDEX'
    }

    @st.cache_data(ttl=60)
    def load_rrg_data():
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=100)
        df_dict = {}
        for name, sym in sectors.items():
            payload = {"symbol": sym, "resolution": "1D", "date_format": "1", "range_from": start_date.strftime("%Y-%m-%d"), "range_to": end_date.strftime("%Y-%m-%d"), "cont_flag": "1"}
            res = fyers.history(data=payload)
            if res.get('s') == 'ok':
                df_dict[name] = pd.Series([candle[4] for candle in res['candles']])
        return pd.DataFrame(df_dict)

    with st.spinner('RRG డేటా లోడ్ అవుతోంది... ⚡'):
        data = load_rrg_data()
        
    if not data.empty:
        nifty_close = data['NIFTY 50'].dropna().reset_index(drop=True)
        bench_roc = ((nifty_close.iloc[-1] - nifty_close.iloc[-21]) / nifty_close.iloc[-21]) * 100
        results = []
        for name, sym in sectors.items():
            if name == 'NIFTY 50' or name not in data.columns: continue
            sec_close = data[name].dropna().reset_index(drop=True)
            if len(sec_close) < 25: continue
            
            sec_roc = ((sec_close.iloc[-1] - sec_close.iloc[-21]) / sec_close.iloc[-21]) * 100
            rs = sec_close / nifty_close
            rs_ratio = 100 + ((rs - rs.rolling(20).mean()) / rs.rolling(20).std()) * 5
            rs_mom = 100 + ((rs_ratio - rs_ratio.rolling(20).mean()) / rs_ratio.rolling(20).std()) * 5
            
            c_rat, c_mom = round(float(rs_ratio.iloc[-1]), 2), round(float(rs_mom.iloc[-1]), 2)
            phase = "LEADING" if c_rat>=100 and c_mom>=100 else "WEAKENING" if c_rat>=100 and c_mom<100 else "LAGGING" if c_rat<100 and c_mom<100 else "IMPROVING"
            results.append({'Sector': name, 'Phase': phase, 'RS-Ratio': c_rat, 'RS-Mom': c_mom, '% Chg (ROC)': round(sec_roc,2)})

        df = pd.DataFrame(results).sort_values(by=['RS-Ratio', 'RS-Mom'], ascending=[False, False]).reset_index(drop=True)
        def highlight(val):
            color = '#00ff00' if val == 'LEADING' else '#ff9900' if val == 'WEAKENING' else '#ff0000' if val == 'LAGGING' else '#00ccff'
            return f'background-color: {color}; color: black; font-weight: bold;'
        st.dataframe(df.style.map(highlight, subset=['Phase']), use_container_width=True)

# ------------------------------------------
# TAB 2: LIVE CHARTS
# ------------------------------------------
with tab2:
    st.header("📈 ఇంట్రాడే లైవ్ చార్ట్స్")
    chart_col1, chart_col2, chart_col3 = st.columns([2, 2, 1])
    
    chart_sym_name = chart_col1.selectbox("చార్ట్ సింబల్:", list(sectors.keys()) + ["RELIANCE", "HDFCBANK", "SBIN"])
    
    # సింబల్ మ్యాపింగ్
    if chart_sym_name in sectors: chart_sym = sectors[chart_sym_name]
    else: chart_sym = f"NSE:{chart_sym_name}-EQ"
        
    res_dict = {'1 Min': '1', '5 Min': '5', '15 Min': '15', 'Daily': '1D'}
    chart_res_name = chart_col2.selectbox("టైమ్‌ఫ్రేమ్:", list(res_dict.keys()), index=1)
    chart_res = res_dict[chart_res_name]
    
    if chart_col3.button("🔄 చార్ట్ రిఫ్రెష్"): st.cache_data.clear()

    @st.cache_data(ttl=30) # 30 సెకన్లకు ఒకసారి రిఫ్రెష్
    def get_live_chart(symbol, resolution):
        end = datetime.date.today()
        start = end - datetime.timedelta(days=5 if resolution != '1D' else 100)
        payload = {"symbol": symbol, "resolution": resolution, "date_format": "1", "range_from": start.strftime("%Y-%m-%d"), "range_to": end.strftime("%Y-%m-%d"), "cont_flag": "1"}
        res = fyers.history(data=payload)
        if res.get('s') == 'ok':
            d = pd.DataFrame(res['candles'], columns=['epoch', 'Open', 'High', 'Low', 'Close', 'Volume'])
            d['Date'] = pd.to_datetime(d['epoch'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
            return d
        return pd.DataFrame()

    c_data = get_live_chart(chart_sym, chart_res)
    if not c_data.empty:
        fig = go.Figure(data=[go.Candlestick(x=c_data['Date'], open=c_data['Open'], high=c_data['High'], low=c_data['Low'], close=c_data['Close'])])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0, r=0, t=30, b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"📌 **{chart_sym_name}** Current LTP: **{c_data['Close'].iloc[-1]:.2f}**")

# ------------------------------------------
# TAB 3: PRO AUTO-BOT (Fix చేసాను)
# ------------------------------------------
with tab3:
    st.header("🤖 Pro Auto-Bot (Live Execution)")
    if 'in_position' not in st.session_state: st.session_state.in_position = False
    if 'entry_price' not in st.session_state: st.session_state.entry_price = 0.0

    algo_col1, algo_col2, algo_col3, algo_col4 = st.columns(4)
    
    # 🌟 డ్రాప్‌డౌన్ ఫిక్స్ 🌟
    popular_symbols = ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX", "NSE:SBIN-EQ", "NSE:RELIANCE-EQ"]
    sym_type = algo_col1.radio("సింబల్ ఎంపిక:", ["లిస్ట్ నుండి", "మాన్యువల్ గా టైప్"])
    if sym_type == "లిస్ట్ నుండి": trade_symbol = algo_col1.selectbox("సింబల్:", popular_symbols)
    else: trade_symbol = algo_col1.text_input("సింబల్ టైప్ చేయండి:", "NSE:NIFTY26MAR22500CE")
    
    trade_qty = algo_col2.number_input("క్వాంటిటీ:", min_value=1, value=15) # Nifty 1 lot
    sl_pts = algo_col3.number_input("Stop Loss (Points):", min_value=1, value=10)
    tp_pts = algo_col4.number_input("Target (Points):", min_value=1, value=20)

    bot = ProAlgoBot(fyers_client=fyers, symbol=trade_symbol, qty=trade_qty, sl_points=sl_pts, tp_points=tp_pts)

    st.markdown("---")
    ctrl_col, stat_col = st.columns(2)

    with ctrl_col:
        st.subheader("Manual Override")
        if st.button("🟢 BUY (Long)"):
            if not st.session_state.in_position:
                if bot.execute_market_order("BUY"):
                    st.session_state.in_position = True
                    st.session_state.entry_price = 100.00 # Demo
                    st.success("✅ లాంగ్ పొజిషన్ ఓపెన్ చేసాం!")
            else: st.warning("మీరు ఇప్పటికే ట్రేడ్ లో ఉన్నారు!")

        if st.button("🔴 SELL (Exit/Short)"):
            if st.session_state.in_position:
                if bot.execute_market_order("SELL"):
                    st.session_state.in_position = False
                    st.session_state.entry_price = 0.0
                    st.error("🛑 ట్రేడ్ క్లోజ్ చేసాం (ఎగ్జిట్)!")

    with stat_col:
        st.subheader("Bot Status")
        if st.session_state.in_position:
            st.info("🟢 **Active Trade Running...**")
            st.write(f"**Symbol:** {trade_symbol}")
            st.write(f"**SL:** {st.session_state.entry_price - sl_pts} | **Target:** {st.session_state.entry_price + tp_pts}")
        else:
            st.warning("🟡 బొట్ స్లీప్ మోడ్‌లో ఉంది. సిగ్నల్స్ కోసం వెతుకుతోంది.")
