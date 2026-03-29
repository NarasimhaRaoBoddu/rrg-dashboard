import streamlit as st
import yfinance as yf
import pandas as pd

# 1. App Page Settings
st.set_page_config(page_title="Ultimate 7989 RRG", page_icon="📈", layout="wide")
st.title("📊 Ultimate 7989 RRG Dashboard")
st.markdown("Live RRG (Relative Rotation Graph) & ROC Momentum Dashboard for NSE Sectors")

# 2. Sector List (Working Yahoo Finance Symbols only)
sectors = {
    'NIFTY 50': '^NSEI', 'BANK': '^NSEBANK', 'IT': '^CNXIT', 'AUTO': '^CNXAUTO',
    'METAL': '^CNXMETAL', 'FMCG': '^CNXFMCG', 'PHARMA': '^CNXPHARMA', 
    'ENERGY': '^CNXENERGY', 'REALTY': '^CNXREALTY', 'MEDIA': '^CNXMEDIA', 
    'INFRA': '^CNXINFRA', 'PSE': '^CNXPSE'
}

# 3. Data Download Function (Cached for performance)
@st.cache_data(ttl=300) # Fetches new data every 5 minutes
def load_data():
    tickers = list(sectors.values())
    data = yf.download(tickers, period="3mo", interval="1d", progress=False)['Close']
    return data

try:
    with st.spinner('Scanning live market data... ⏳'):
        data = load_data()

    rrg_len = 20
    roc_lookback = 20
    results = []

    # Benchmark (Nifty) Calculations
    nifty_close = data[sectors['NIFTY 50']].squeeze()
    bench_roc = ((nifty_close.iloc[-1] - nifty_close.iloc[-roc_lookback-1]) / nifty_close.iloc[-roc_lookback-1]) * 100

    # 4. Calculate Stats for All Sectors
    for name, sym in sectors.items():
        if name == 'NIFTY 50': continue
        
        sec_close = data[sym].squeeze()
        
        # ROC Math
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
        
        # Phase Identification
        if cur_ratio >= 100 and cur_mom >= 100: phase = "LEADING"
        elif cur_ratio >= 100 and cur_mom < 100: phase = "WEAKENING"
        elif cur_ratio < 100 and cur_mom < 100: phase = "LAGGING"
        else: phase = "IMPROVING"

        results.append({
            'Sector': name, 'Phase': phase, 'RS-Ratio': cur_ratio, 
            'RS-Mom': cur_mom, '% Chg (ROC)': cur_roc, 'vs Nifty': vs_nifty
        })

    # 5. DataFrame Formatting & Sorting by Score
    df = pd.DataFrame(results)
    df['Score'] = df['RS-Ratio'] + df['RS-Mom'] + df['% Chg (ROC)']
    df = df.sort_values(by='Score', ascending=False).drop(columns=['Score']).reset_index(drop=True)

    # 6. Styling Functions
    def highlight_phase(val):
        color = '#00ff00' if val == 'LEADING' else '#ff9900' if val == 'WEAKENING' else '#ff0000' if val == 'LAGGING' else '#00ccff'
        return f'background-color: {color}; color: black; font-weight: bold;'
    
    def color_roc(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}; font-weight: bold;'

    # Apply styling
    styled_df = df.style.map(highlight_phase, subset=['Phase']) \
                        .map(color_roc, subset=['% Chg (ROC)', 'vs Nifty'])

    # Dashboard Display
    st.markdown(f"**NIFTY 50 Current ROC:** `{bench_roc:.2f}%`")
    st.dataframe(styled_df, use_container_width=True, height=500)

    # Highlight Top Sector
    top_sector = df.iloc[0]
    st.success(f"🚀 **ALERT:** The **{top_sector['Sector']}** sector is currently in the **{top_sector['Phase']}** phase and is leading the market!")

except Exception as e:
    st.error(f"Error fetching data: {e}")

except Exception as e:
    st.error(f"డేటా లాగడంలో ఎర్రర్ వచ్చింది: {e}")
