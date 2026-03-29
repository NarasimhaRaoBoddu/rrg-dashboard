import streamlit as st
import pandas as pd
import datetime
from fyers_apiv3 import fyersModel

# ==========================================
# 1. APP SETTINGS & FYERS LOGIN
# ==========================================
st.set_page_config(page_title="Ultimate 7989 RRG & Algo", page_icon="📈", layout="wide")
st.title("📊 Ultimate 7989 RRG Dashboard + Pro Algo Bot")
st.markdown("Live Sector Rotation & Automated Order Execution System - Direct Broker Data")

# మీ డీటెయిల్స్ ఇక్కడ పేస్ట్ చేయండి
CLIENT_ID = "QHIBBNGEQE-100"      
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCcHlQUlhBTUpsRXduZERZczBjWGJmT0MwRXN4X3ZDaHVfdThPQnlVcFJFbTdJNU5tQXdiZjdVSFFNdVM1cTBzU1hsZkpzVWd0V0R3eENsemEtSzJKRnBrV19LbE5KX1lobVNCbTJWZEItdERPTzJ4TT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiIxOTk3NWUyOGVlZjQ0YWM4YzE3NGE3MjQyYjgzNjlhMWM4YzE0ZGVkMWRiMjFkYTNlOGI4M2U0MSIsImlzRGRwaUVuYWJsZWQiOiJZIiwiaXNNdGZFbmFibGVkIjoiWSIsImZ5X2lkIjoiWU4xMTU5MSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzc0ODMwNjAwLCJpYXQiOjE3NzQ3Nzc0MzEsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc3NDc3NzQzMSwic3ViIjoiYWNjZXNzX3Rva2VuIn0.cwiru3JptArYldschrXS0QuskKKvpMMjxVj94wkTmgI"    

try:
    # Fyers సర్వర్ కి కనెక్ట్ అవ్వడం
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
        
        # నిజంగా Fyers లో ఆర్డర్ వెళ్లాలంటే ఈ కింది కామెంట్స్ (#) తీసేయండి
        # try:
        #     res = self.fyers.place_order(data=order_data)
        #     if res.get('s') == 'ok': 
        #         st.toast(f"✅ {side_text} ఆర్డర్ Fyers కి వెళ్ళింది!")
        #         return True
        #     else:
        #         st.error(f"❌ ఆర్డర్ ఫెయిల్: {res.get('message')}")
        #         return False
        # except Exception as e:
        #     st.error(f"API Error: {e}")
        #     return False

        # ప్రస్తుతానికి Paper Trading (టెస్టింగ్) కోసం:
        st.toast(f"✅ (TEST) {side_text} ఆర్డర్ పంపబడింది! {self.symbol}")
        return True

# ==========================================
# 3. TABS SETUP (UI డిజైన్)
# ==========================================
tab1, tab2 = st.tabs(["📊 RRG డాష్‌బోర్డ్", "🤖 Pro Auto-Bot"])

# ------------------------------------------
# TAB 1: RRG DASHBOARD
# ------------------------------------------
with tab1:
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
    def load_fyers_data():
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=100)
        df_dict = {}
        error_msg = None
        for name, sym in sectors.items():
            payload = {
                "symbol": sym, "resolution": "1D", "date_format": "1",
                "range_from": start_date.strftime("%Y-%m-%d"),
                "range_to": end_date.strftime("%Y-%m-%d"), "cont_flag": "1"
            }
            res = fyers.history(data=payload)
            if res.get('s') == 'ok':
                closes = [candle[4] for candle in res['candles']]
                df_dict[name] = pd.Series(closes)
            else:
                error_msg = f"Error for {sym}: {res}"
                break 
        return pd.DataFrame(df_dict), error_msg

    try:
        with st.spinner('మార్కెట్ లైవ్ డేటాని స్కాన్ చేస్తున్నాను... ⚡'):
            data, api_error = load_fyers_data()

        if api_error:
            st.error(f"🔴 FYERS SERVER ERROR: {api_error}")
        elif data.empty:
            st.error("డేటా రాలేదు సార్. ఖాళీగా ఉంది.")
        else:
            rrg_len = 20
            roc_lookback = 20
            results = []

            nifty_close = data['NIFTY 50'].dropna().reset_index(drop=True)
            bench_roc = ((nifty_close.iloc[-1] - nifty_close.iloc[-roc_lookback-1]) / nifty_close.iloc[-roc_lookback-1]) * 100

            for name, sym in sectors.items():
                if name == 'NIFTY 50': continue
                if name not in data.columns: continue
                
                sec_close = data[name].dropna().reset_index(drop=True)
                if len(sec_close) < rrg_len + 5: continue
                
                # ROC & RRG Math
                sec_roc = ((sec_close.iloc[-1] - sec_close.iloc[-roc_lookback-1]) / sec_close.iloc[-roc_lookback-1]) * 100
                vs_nifty = sec_roc - bench_roc
                rs = sec_close / nifty_close
                rs_mean = rs.rolling(window=rrg_len).mean()
                rs_dev = rs.rolling(window=rrg_len).std()
                rs_ratio = 100 + ((rs - rs_mean) / rs_dev) * 5
                rat_mean = rs_ratio.rolling(window=rrg_len).mean()
                rat_dev = rs_ratio.rolling(window=rrg_len).std()
                rs_mom = 100 + ((rs_ratio - rat_mean) / rat_dev) * 5
                
                cur_ratio = round(float(rs_ratio.iloc[-1]), 2)
                cur_mom = round(float(rs_mom.iloc[-1]), 2)
                cur_roc = round(float(sec_roc), 2)
                vs_nifty = round(float(vs_nifty), 2)
                
                # Phase
                if cur_ratio >= 100 and cur_mom >= 100: phase = "LEADING"
                elif cur_ratio >= 100 and cur_mom < 100: phase = "WEAKENING"
                elif cur_ratio < 100 and cur_mom < 100: phase = "LAGGING"
                else: phase = "IMPROVING"

                results.append({
                    'Sector': name, 'Phase': phase, 'RS-Ratio': cur_ratio, 
                    'RS-Mom': cur_mom, '% Chg (ROC)': cur_roc, 'vs Nifty': vs_nifty
                })

            df = pd.DataFrame(results)
            df['Score'] = df['RS-Ratio'] + df['RS-Mom'] + df['% Chg (ROC)']
            df = df.sort_values(by='Score', ascending=False).drop(columns=['Score']).reset_index(drop=True)

            def highlight_phase(val):
                color = '#00ff00' if val == 'LEADING' else '#ff9900' if val == 'WEAKENING' else '#ff0000' if val == 'LAGGING' else '#00ccff'
                return f'background-color: {color}; color: black; font-weight: bold;'
            
            def color_roc(val):
                return 'color: green; font-weight: bold;' if val > 0 else 'color: red; font-weight: bold;'

            styled_df = df.style.map(highlight_phase, subset=['Phase']).map(color_roc, subset=['% Chg (ROC)', 'vs Nifty'])

            st.markdown(f"**NIFTY 50 ప్రస్తుత ROC:** `{bench_roc:.2f}%`")
            st.dataframe(styled_df, use_container_width=True, height=500)

    except Exception as e:
        st.error(f"డాష్‌బోర్డ్ ఎర్రర్: {e}")

# ------------------------------------------
# TAB 2: PRO AUTO-BOT UI
# ------------------------------------------
with tab2:
    st.header("🤖 Pro Level Auto-Bot (Live Execution)")
    st.markdown("ఇక్కడ మీరు ఏ స్టాక్ లేదా ఆప్షన్ సింబల్ ఇచ్చినా, అది ఆటోమెటిక్ గా ట్రేడ్ తీసుకునేలా చేయవచ్చు.")

    # Session State (మెమరీ)
    if 'in_position' not in st.session_state:
        st.session_state.in_position = False
    if 'entry_price' not in st.session_state:
        st.session_state.entry_price = 0.0

    col1, col2, col3, col4 = st.columns(4)
    trade_symbol = col1.text_input("ట్రేడ్ సింబల్:", "NSE:SBIN-EQ")
    trade_qty = col2.number_input("క్వాంటిటీ:", min_value=1, value=1)
    sl_pts = col3.number_input("Stop Loss (Points):", min_value=1, value=10)
    tp_pts = col4.number_input("Target (Points):", min_value=1, value=20)

    # Bot Initialization (టైపో ఫిక్స్ చేశాం: fyers_client)
    bot = ProAlgoBot(fyers_client=fyers, symbol=trade_symbol, qty=trade_qty, sl_points=sl_pts, tp_points=tp_pts)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Manual Override (కంట్రోల్స్)")
        if st.button("🟢 BUY (Long) Order"):
            if not st.session_state.in_position:
                if bot.execute_market_order("BUY"):
                    st.session_state.in_position = True
                    st.session_state.entry_price = 500.00 # Demo entry price
                    st.success("✅ లాంగ్ పొజిషన్ ఓపెన్ చేసాం!")
            else:
                st.warning("మీరు ఇప్పటికే ట్రేడ్ లో ఉన్నారు!")

        if st.button("🔴 SELL (Exit/Short) Order"):
            if st.session_state.in_position:
                if bot.execute_market_order("SELL"):
                    st.session_state.in_position = False
                    st.session_state.entry_price = 0.0
                    st.error("🛑 ట్రేడ్ క్లోజ్ చేసాం (ఎగ్జిట్)!")

    with col_b:
        st.subheader("Bot Status (స్టేటస్)")
        if st.session_state.in_position:
            st.info("🟢 **Active Trade Running...**")
            st.write(f"**Entry Price:** {st.session_state.entry_price}")
            st.write(f"**Stop Loss:** {st.session_state.entry_price - sl_pts}")
            st.write(f"**Target:** {st.session_state.entry_price + tp_pts}")
        else:
            st.warning("🟡 బొట్ స్లీప్ మోడ్‌లో ఉంది (No Active Trades). సిగ్నల్స్ కోసం వెతుకుతోంది.")
