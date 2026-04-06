import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from dhanhq import dhanhq

# ==========================================
# 1. APP SETTINGS & DHAN LOGIN (SECRETS)
# ==========================================
st.set_page_config(page_title="Ultimate Dhan Terminal", page_icon="⚡", layout="wide")
st.title("⚡ Ultimate Dhan Live Trading Terminal")
st.markdown("Stock Rotation | Live Charts | Fastest Auto-Bot Execution - Dhan API")

# 🔒 సెక్యూరిటీ కోసం కీస్ ని secrets నుండి లాగుతున్నాం
try:
    CLIENT_ID = st.secrets[DHAN_CLIENT_ID]
    ACCESS_TOKEN = st.secrets["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzc1NTgzOTg3LCJpYXQiOjE3NzU0OTc1ODcsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTA3MjY1OTIwIn0.q1Mv45QchrzXLELZB1XSKsWlG8Kpdh4iBVabMsMjrgfGl2sOYk3jO9eZMJgpEooU1xAXf-b4ef57lAah5ul0_g"]
    
    # Dhan కి కనెక్ట్ అవ్వడం
    dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)
    funds = dhan.get_fund_limits()
    if funds.get('status') == 'success':
        st.sidebar.success("✅ Dhan API కనెక్షన్ సక్సెస్!")
    else:
        st.sidebar.error("❌ Dhan లాగిన్ ఫెయిల్ అయ్యింది.")
except Exception as e:
    st.error(f"లాగిన్ ఎర్రర్. st.secrets సెట్ చేశారో లేదో చెక్ చేయండి. Error: {e}")
    st.stop()

# ==========================================
# 2. DHAN PRO ALGO BOT CLASS (మెదడు)
# ==========================================
class DhanAlgoBot:
    def __init__(self, dhan_client, sec_id, exchange, qty, sl_points, tp_points):
        self.dhan = dhan_client
        self.sec_id = str(sec_id)  # Dhan లో ఆర్డర్స్ కి ID ముఖ్యం (ఉదా: 1333)
        self.exchange = exchange   # ఉదా: dhan.NSE_EQ లేదా dhan.NSE_FNO
        self.qty = qty
        self.sl_points = sl_points
        self.tp_points = tp_points

    def execute_market_order(self, side_text):
        txn_type = self.dhan.BUY if side_text == "BUY" else self.dhan.SELL
        
        try:
            # నిజంగా ఆర్డర్ వెళ్లాలంటే ఈ కింద ఉన్న కామెంట్స్ (#) తీసేయండి
            # res = self.dhan.place_order(
            #     security_id=self.sec_id, exchange_segment=self.exchange,
            #     transaction_type=txn_type, quantity=self.qty,
            #     order_type=self.dhan.MARKET, product_type=self.dhan.INTRADAY, price=0
            # )
            # if res.get('status') == 'success':
            #     st.toast(f"✅ {side_text} ఆర్డర్ Dhan కి వెళ్ళింది! (ID: {res['data']['orderId']})")
            #     return True
            # else:
            #     st.error(f"❌ ఆర్డర్ ఫెయిల్: {res.get('remarks')}")
            #     return False
            
            # టెస్టింగ్ మెసేజ్:
            st.toast(f"✅ (LIVE TEST) {side_text} ఆర్డర్ ఎగ్జిక్యూట్ అయ్యింది! Sec ID: {self.sec_id}")
            return True
            
        except Exception as e:
            st.error(f"API Error: {e}")
            return False

# ==========================================
# 3. MEGA TERMINAL TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["📊 1. టాప్ స్టాక్స్ రొటేషన్", "📈 2. లైవ్ చార్ట్స్", "🤖 3. ప్రో ఆటో-బోట్ (Fast)"])

# పాపులర్ స్టాక్స్ వాటి Dhan Security IDs
top_stocks = {
    'HDFC BANK': '1333', 'RELIANCE': '2885', 'SBI': '4329', 
    'TCS': '11536', 'INFY': '1594', 'ICICI BANK': '4963', 
    'AXIS BANK': '5900', 'KOTAK BANK': '1922', 'ITC': '1660'
}

# ------------------------------------------
# TAB 1: RRG DASHBOARD (Top Stocks)
# ------------------------------------------
with tab1:
    st.header("నిఫ్టీ టాప్ స్టాక్స్ రొటేషన్ (Live RS & Momentum)")
    
    @st.cache_data(ttl=60)
    def load_dhan_historical():
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=100)
        df_dict = {}
        
        # ముందుగా నిఫ్టీ (NIFTY 50) డేటా లాగడం బెంచ్ మార్క్ కోసం
        res_nifty = dhan.historical_daily_data(symbol='NIFTY 50', exchange_segment='IDX', instrument_type='INDEX', expiry_code=0, from_date=start_date.strftime("%Y-%m-%d"), to_date=end_date.strftime("%Y-%m-%d"))
        if res_nifty.get('status') == 'success':
            nifty_close = pd.Series(res_nifty['data']['close'])
        else:
            return pd.DataFrame(), pd.Series()

        for name in top_stocks.keys():
            res = dhan.historical_daily_data(symbol=name.replace(" ", ""), exchange_segment='NSE_EQ', instrument_type='EQUITY', expiry_code=0, from_date=start_date.strftime("%Y-%m-%d"), to_date=end_date.strftime("%Y-%m-%d"))
            if res.get('status') == 'success':
                df_dict[name] = pd.Series(res['data']['close'])
        
        return pd.DataFrame(df_dict), nifty_close

    with st.spinner('Dhan సర్వర్ నుండి RRG డేటా లాగుతున్నాను... ⚡'):
        data, nifty_data = load_dhan_historical()
        
    if not data.empty and not nifty_data.empty:
        nifty_close = nifty_data.dropna().reset_index(drop=True)
        bench_roc = ((nifty_close.iloc[-1] - nifty_close.iloc[-21]) / nifty_close.iloc[-21]) * 100
        results = []
        for name in top_stocks.keys():
            if name not in data.columns: continue
            sec_close = data[name].dropna().reset_index(drop=True)
            if len(sec_close) < 25: continue
            
            sec_roc = ((sec_close.iloc[-1] - sec_close.iloc[-21]) / sec_close.iloc[-21]) * 100
            
            # RS & Momentum
            rs = sec_close / nifty_close
            rs_ratio = 100 + ((rs - rs.rolling(20).mean()) / rs.rolling(20).std()) * 5
            rs_mom = 100 + ((rs_ratio - rs_ratio.rolling(20).mean()) / rs_ratio.rolling(20).std()) * 5
            
            c_rat, c_mom = round(float(rs_ratio.iloc[-1]), 2), round(float(rs_mom.iloc[-1]), 2)
            phase = "LEADING" if c_rat>=100 and c_mom>=100 else "WEAKENING" if c_rat>=100 and c_mom<100 else "LAGGING" if c_rat<100 and c_mom<100 else "IMPROVING"
            results.append({'Stock': name, 'Phase': phase, 'RS-Ratio': c_rat, 'RS-Mom': c_mom, '% Chg (ROC)': round(sec_roc,2)})

        df = pd.DataFrame(results).sort_values(by=['RS-Ratio', 'RS-Mom'], ascending=[False, False]).reset_index(drop=True)
        def highlight(val):
            color = '#00ff00' if val == 'LEADING' else '#ff9900' if val == 'WEAKENING' else '#ff0000' if val == 'LAGGING' else '#00ccff'
            return f'background-color: {color}; color: black; font-weight: bold;'
        st.dataframe(df.style.map(highlight, subset=['Phase']), use_container_width=True)

# ------------------------------------------
# TAB 2: LIVE CHARTS
# ------------------------------------------
with tab2:
    st.header("📈 Dhan ఇంట్రాడే లైవ్ చార్ట్స్")
    chart_col1, chart_col2 = st.columns([3, 1])
    
    chart_sym = chart_col1.selectbox("చార్ట్ కోసం స్టాక్ సెలెక్ట్ చేయండి:", list(top_stocks.keys()))
    if chart_col2.button("🔄 చార్ట్ రిఫ్రెష్"): st.cache_data.clear()

    @st.cache_data(ttl=30)
    def get_live_chart_dhan(symbol):
        end = datetime.date.today()
        start = end - datetime.timedelta(days=5) # 5 రోజులు ఇంట్రాడే డేటా
        res = dhan.historical_minute_charts(symbol=symbol.replace(" ", ""), exchange_segment='NSE_EQ', instrument_type='EQUITY', from_date=start.strftime("%Y-%m-%d"), to_date=end.strftime("%Y-%m-%d"))
        
        if res.get('status') == 'success':
            d = pd.DataFrame(res['data'])
            # కాలమ్స్ ని క్యాపిటల్స్ కి మార్చడం (Plotly కోసం)
            d.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'start_Time': 'epoch'}, inplace=True)
            d['Date'] = pd.to_datetime(d['epoch']) # Dhan లో డైరెక్ట్ గా డేట్ ఫార్మాట్ లోనే వస్తుంది
            return d
        return pd.DataFrame()

    c_data = get_live_chart_dhan(chart_sym)
    if not c_data.empty:
        fig = go.Figure(data=[go.Candlestick(x=c_data['Date'], open=c_data['Open'], high=c_data['High'], low=c_data['Low'], close=c_data['Close'])])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0, r=0, t=30, b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"📌 **{chart_sym}** Current LTP: **{c_data['Close'].iloc[-1]:.2f}**")
    else:
        st.warning("మార్కెట్ క్లోజ్ అయినందువల్ల ఈరోజు 1 నిమిషం డేటా రాలేదు. ఉదయం లైవ్ లో చెక్ చేయండి.")

# ------------------------------------------
# TAB 3: DHAN SCALPING AUTO-BOT
# ------------------------------------------
with tab3:
    st.header("🤖 Dhan Auto-Bot (Flash Execution)")
    st.info("💡 సూచన: వేగంగా ఆర్డర్ కొట్టడానికి Dhan లో Security ID వాడతాము. ఉదా: HDFC కి 1333, Reliance కి 2885, SBI కి 4329.")
    
    if 'in_position' not in st.session_state: st.session_state.in_position = False
    if 'entry_price' not in st.session_state: st.session_state.entry_price = 0.0

    algo_col1, algo_col2, algo_col3, algo_col4 = st.columns(4)
    
    trade_sec_id = algo_col1.text_input("Security ID:", "1333")
    trade_qty = algo_col2.number_input("క్వాంటిటీ:", min_value=1, value=1) 
    sl_pts = algo_col3.number_input("Stop Loss (Points):", min_value=1, value=5)
    tp_pts = algo_col4.number_input("Target (Points):", min_value=1, value=10)

    bot = DhanAlgoBot(dhan_client=dhan, sec_id=trade_sec_id, exchange=dhan.NSE_EQ, qty=trade_qty, sl_points=sl_pts, tp_points=tp_pts)

    st.markdown("---")
    ctrl_col, stat_col = st.columns(2)

    with ctrl_col:
        st.subheader("Flash Controls")
        if st.button("🟢 BUY (Market)", use_container_width=True):
            if not st.session_state.in_position:
                if bot.execute_market_order("BUY"):
                    st.session_state.in_position = True
                    st.session_state.entry_price = 100.00 # డెమో ప్రైస్
                    st.success("✅ లాంగ్ పొజిషన్ ఓపెన్ చేసాం!")
            else: st.warning("మీరు ఇప్పటికే ట్రేడ్ లో ఉన్నారు!")

        if st.button("🔴 SELL (Exit)", use_container_width=True):
            if st.session_state.in_position:
                if bot.execute_market_order("SELL"):
                    st.session_state.in_position = False
                    st.session_state.entry_price = 0.0
                    st.error("🛑 ట్రేడ్ క్లోజ్ చేసాం (ఎగ్జిట్)!")

with stat_col:
        st.subheader("Bot Status")
        if st.session_state.in_position:
            st.info("🟢 **Active Trade Running...**")
            st.write(f"**Security ID:** {trade_sec_id}") # (Fyers అయితే trade_symbol అని ఉంటుంది)
            st.write(f"**SL:** {st.session_state.entry_price - sl_pts} | **Target:** {st.session_state.entry_price + tp_pts}")
        else:
            st.warning("🟡 బొట్ స్లీప్ మోడ్‌లో ఉంది. రెడీ గా ఉండండి.")
