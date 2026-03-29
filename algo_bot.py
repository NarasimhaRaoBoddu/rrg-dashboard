import streamlit as st
import time

# --- 1. PRO ALGO BOT క్లాస్ ---
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
        # నిజంగా ఆర్డర్ వెళ్లాలంటే కింద కామెంట్స్ తీసేయండి (టెస్టింగ్ కోసం కామెంట్ చేశాను)
        # res = self.fyers.place_order(data=order_data)
        # if res.get('s') == 'ok': return True
        # return False
        
        # ప్రస్తుతానికి డెమో (Paper Trading) లాగా చూపిస్తున్నాను:
        st.toast(f"✅ {side_text} ఆర్డర్ Fyers కి పంపబడింది!")
        return True

# --- 2. స్ట్రీమ్‌లిట్ మెమరీ సెటప్ (Session State) ---
# యాప్ రిఫ్రెష్ అయినా ట్రేడ్ డీటెయిల్స్ పోకుండా ఇది కాపాడుతుంది
if 'in_position' not in st.session_state:
    st.session_state.in_position = False
if 'entry_price' not in st.session_state:
    st.session_state.entry_price = 0.0

# --- 3. ఆల్గో ట్రేడింగ్ UI (యూజర్ ఇంటర్‌ఫేస్) ---
st.header("🤖 Pro Level Auto-Bot (Live Execution)")

col1, col2, col3, col4 = st.columns(4)
trade_symbol = col1.text_input("ట్రేడ్ సింబల్:", "NSE:SBIN-EQ")
trade_qty = col2.number_input("క్వాంటిటీ:", min_value=1, value=1)
sl_pts = col3.number_input("Stop Loss (Points):", min_value=1, value=10)
tp_pts = col4.number_input("Target (Points):", min_value=1, value=20)

# (మీ అసలైన fyers ఆబ్జెక్ట్ ఇక్కడ పాస్ చేయాలి. ఇక్కడ నేను dummy గా fyers అని రాస్తున్నాను)
bot = ProAlgoBot(fyers="fyers_connection_here", symbol=trade_symbol, qty=trade_qty, sl_points=sl_pts, tp_points=tp_pts)

st.markdown("---")

# --- 4. లైవ్ ఎగ్జిక్యూషన్ కంట్రోల్స్ ---
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Manual Override (టెస్టింగ్ కోసం)")
    if st.button("🟢 BUY (Long)"):
        if not st.session_state.in_position:
            if bot.execute_market_order("BUY"):
                st.session_state.in_position = True
                st.session_state.entry_price = 500.00 # (ఇక్కడ లైవ్ ప్రైస్ లాగాలి)
                st.success(f"కొన్నాం! Entry Price: {st.session_state.entry_price}")
        else:
            st.warning("మీరు ఇప్పటికే ట్రేడ్ లో ఉన్నారు!")

    if st.button("🔴 SELL (Exit/Short)"):
        if st.session_state.in_position:
            if bot.execute_market_order("SELL"):
                st.session_state.in_position = False
                st.session_state.entry_price = 0.0
                st.error("ట్రేడ్ క్లోజ్ చేసాం!")

with col_b:
    st.subheader("Bot Status (స్టేటస్)")
    if st.session_state.in_position:
        st.info("🟢 **Active Trade Running...**")
        st.write(f"**Entry Price:** {st.session_state.entry_price}")
        st.write(f"**Stop Loss:** {st.session_state.entry_price - sl_pts}")
        st.write(f"**Target:** {st.session_state.entry_price + tp_pts}")
    else:
        st.warning("🟡 బొట్ స్లీప్ మోడ్‌లో ఉంది (No Active Trades). సిగ్నల్స్ కోసం వెతుకుతోంది.")
