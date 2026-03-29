import streamlit as st
import pandas as pd
import datetime
from fyers_apiv3 import fyersModel

# 1. App Page Settings
st.set_page_config(page_title="Ultimate 7989 RRG", page_icon="📈", layout="wide")
st.title("📊 Ultimate 7989 RRG Dashboard (Fyers Live)")
st.markdown("Live RRG & ROC Momentum Dashboard for NSE Sectors - Direct Broker Data")

# ==========================================
# 2. FYERS CREDENTIALS (PASTE YOUR DETAILS HERE)
# ==========================================
CLIENT_ID = "QHIBBNGEQE-100"      # Example: "QHIBBNGEQE-100"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCcHlQUlhBTUpsRXduZERZczBjWGJmT0MwRXN4X3ZDaHVfdThPQnlVcFJFbTdJNU5tQXdiZjdVSFFNdVM1cTBzU1hsZkpzVWd0V0R3eENsemEtSzJKRnBrV19LbE5KX1lobVNCbTJWZEItdERPTzJ4TT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiIxOTk3NWUyOGVlZjQ0YWM4YzE3NGE3MjQyYjgzNjlhMWM4YzE0ZGVkMWRiMjFkYTNlOGI4M2U0MSIsImlzRGRwaUVuYWJsZWQiOiJZIiwiaXNNdGZFbmFibGVkIjoiWSIsImZ5X2lkIjoiWU4xMTU5MSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzc0ODMwNjAwLCJpYXQiOjE3NzQ3Nzc0MzEsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc3NDc3NzQzMSwic3ViIjoiYWNjZXNzX3Rva2VuIn0.cwiru3JptArYldschrXS0QuskKKvpMMjxVj94wkTmgI"    # The huge token you generated

# Initialize Fyers API
try:
    fyers = fyersModel.FyersModel(client_id=CLIENT_ID, is_async=False, token=ACCESS_TOKEN, log_path="")
except Exception as e:
    st.error(f"Fyers Login Error: {e}")

# 3. Sector List (Correct Fyers Symbols with Spaces)
sectors = {
    'NIFTY 50': 'NSE:NIFTY50-INDEX', 'BANK': 'NSE:NIFTYBANK-INDEX', 
    'FINSRV': 'NSE:FINNIFTY-INDEX', 'IT': 'NSE:NIFTYIT-INDEX', 
    'AUTO': 'NSE:NIFTYAUTO-INDEX', 'METAL': 'NSE:NIFTYMETAL-INDEX', 
    'FMCG': 'NSE:NIFTYFMCG-INDEX', 'PHARMA': 'NSE:NIFTYPHARMA-INDEX', 
    'ENERGY': 'NSE:NIFTYENERGY-INDEX', 'REALTY': 'NSE:NIFTYREALTY-INDEX', 
    'MEDIA': 'NSE:NIFTYMEDIA-INDEX', 'INFRA': 'NSE:NIFTYINFRA-INDEX', 
    'PSE': 'NSE:NIFTYPSE-INDEX'
}

# 4. Data Fetching Function with Error Catcher
@st.cache_data(ttl=60)
def load_fyers_data():
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=100)
    
    df_dict = {}
    error_msg = None
    
    for name, sym in sectors.items():
        payload = {
            "symbol": sym,
            "resolution": "1D",
            "date_format": "1",
            "range_from": start_date.strftime("%Y-%m-%d"),
            "range_to": end_date.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }
        res = fyers.history(data=payload)
        
        if res.get('s') == 'ok':
            closes = [candle[4] for candle in res['candles']]
            df_dict[name] = pd.Series(closes)
        else:
            error_msg = f"Error for {sym}: {res}"
            break # Stop loop if there's an error
            
    return pd.DataFrame(df_dict), error_msg

try:
    with st.spinner('Fetching lightning fast data from Fyers... ⚡'):
        data, api_error = load_fyers_data()

    if api_error:
        st.error(f"🔴 FYERS SERVER ERROR: {api_error}")
        st.info("Please check if your Token is correct. Remember: Tokens expire every night at 12 AM. You might need to generate a new one using get_token.py")
    elif data.empty:
        st.error("No data received. DataFrame is empty.")
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
            
            # ROC
            sec_roc = ((sec_close.iloc[-1] - sec_close.iloc[-roc_lookback-1]) / sec_close.iloc[-roc_lookback-1]) * 100
            vs_nifty = sec_roc - bench_roc
            
            # RRG Math
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

        st.markdown(f"**NIFTY 50 Current ROC:** `{bench_roc:.2f}%`")
        st.dataframe(styled_df, use_container_width=True, height=500)

        top_sector = df.iloc[0]
        st.success(f"🚀 **ALERT:** **{top_sector['Sector']}** is in **{top_sector['Phase']}** phase and leading the market!")

except Exception as e:
    st.error(f"Dashboard Error: {e}")
