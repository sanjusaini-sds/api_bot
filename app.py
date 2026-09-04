import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🚀 MCX Natural Gas - VWAP + ORB Bot Dashboard")

# स्टेटस कार्ड
st.metric(label="Bot Status", value="Running 🟢", delta="Connected to Angel One")

# लाइव सिग्नल टेबल या लॉग दिखाने के लिए
st.subheader("Live Trading Signals")
log_data = {
    "Time": [datetime.now().strftime("%H:%M:%S")],
    "Symbol": ["Natural Gas (543207)"],
    "Action": ["WAIT"],
    "Price": ["--"]
}
df = pd.DataFrame(log_data)
st.table(df)

if st.button("Refresh Data"):
    st.rerun()