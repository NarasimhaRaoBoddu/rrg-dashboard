import streamlit as st
import yfinance as yf
import pandas as pd

# 1. యాప్ పేజీ సెట్టింగ్స్
st.set_page_config(page_title="Ultimate 7989 RRG", page_icon="📈", layout="wide")
st.title("📊 Ultimate 7989 RRG Dashboard")
st.markdown("నిఫ్టీ 14 సెక్టార్ల లైవ్ రొటేషన్ (RRG) & మొమెంటం (ROC) డాష్‌బోర్డ్")

# సెక్టార్ల లిస్ట్ (Yahoo Finance Symbols)
sectors = {
    'NIFTY 50': '^NSEI', 'BANK': '^NSEBANK', 'IT': '^CNXIT', 'AUTO': '^CNXAUTO',
    'METAL': '^CNXMETAL', 'FMCG': '^CNXFMCG', 'PHARMA': '^CNXPHARMA', 
    'ENERGY': '^CNXENERGY', 'REALTY': '^CNXREALTY', 'MEDIA': '^CNXMEDIA', 
    'INFRA': '^CNXINFRA', 'PSE': '^CNXPSE', 'FINSRV': 'NIFTYFINSERVICE'
}

# 2. డేటా డౌన్‌లోడ్ ఫంక్షన్ (యాప్ ఫాస్ట్ గా ఉండటానికి Cache వాడుతున్నాం)
@st.cache_data(ttl=300) # ప్రతి 5 నిమిషాలకు ఒకసారి మాత్రమే డేటా లాగుతుంది
def load_data():
    tickers = list(sectors.values())
    data = yf.download(tickers, period="3mo", interval="1d", progress=False)['Close']
    return data

try:
    with st.spinner('మార్కెట్ లైవ్ డేటాని స్కాన్ చేస్తున్నాను... ⏳'):
        data = load_data()

    rrg_len = 20
    roc_lookback = 20
    results = []

    # బేంచ్‌మార్క్ (Nifty) లెక్కలు
    nifty_close = data[sectors['NIFTY 50']].squeeze()
    bench_roc = ((nifty_close.iloc[-1] - nifty_close.iloc[-roc_lookback-1]) / nifty_close.iloc[-roc_lookback-1]) * 100

    # 3. అన్ని సెక్టార్ల గణాంకాలు క్యాలిక్యులేట్ చేయడం
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
        
        # Phase కనుక్కోవడం
        if cur_ratio >= 100 and cur_mom >= 100: phase = "LEADING"
        elif cur_ratio >= 100 and cur_mom < 100: phase = "WEAKENING"
        elif cur_ratio < 100 and cur_mom < 100: phase = "LAGGING"
        else: phase = "IMPROVING"

        results.append({
            'Sector': name, 'Phase': phase, 'RS-Ratio': cur_ratio, 
            'RS-Mom': cur_mom, '% Chg (ROC)': cur_roc, 'vs Nifty': vs_nifty
        })

    # 4. డేటాని టేబుల్ లాగా మార్చడం & స్కోర్ ప్రకారం సార్ట్ చేయడం
    df = pd.DataFrame(results)
    df['Score'] = df['RS-Ratio'] + df['RS-Mom'] + df['% Chg (ROC)']
    df = df.sort_values(by='Score', ascending=False).drop(columns=['Score']).reset_index(drop=True)

    # 5. టేబుల్ కి రంగులు అద్దడం (యాప్ లో అందంగా కనిపించడానికి)
    def highlight_phase(val):
        color = '#00ff00' if val == 'LEADING' else '#ff9900' if val == 'WEAKENING' else '#ff0000' if val == 'LAGGING' else '#00ccff'
        return f'background-color: {color}; color: black; font-weight: bold;'
    
    def color_roc(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}; font-weight: bold;'

    styled_df = df.style.applymap(highlight_phase, subset=['Phase']) \
                        .applymap(color_roc, subset=['% Chg (ROC)', 'vs Nifty'])

    # డాష్‌బోర్డ్ ప్రదర్శన
    st.markdown(f"**NIFTY 50 ప్రస్తుత ROC:** `{bench_roc:.2f}%`")
    st.dataframe(styled_df, use_container_width=True, height=500)

    # నంబర్ 1 సెక్టార్ ని హైలైట్ చేయడం
    top_sector = df.iloc[0]
    st.success(f"🚀 **అలెర్ట్:** ప్రస్తుతం **{top_sector['Sector']}** సెక్టార్ {top_sector['Phase']} దశలో ఉండి మార్కెట్ ని లీడ్ చేస్తోంది!")

except Exception as e:
    st.error(f"డేటా లాగడంలో ఎర్రర్ వచ్చింది: {e}")
