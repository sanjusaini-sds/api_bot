import time
from datetime import datetime
import pandas as pd
import numpy as np
import pyotp
from SmartApi.smartConnect import SmartConnect

# Credential Details
API_KEY = "0FAlHyVa"
CLIENT_CODE = "AABX482050"
PIN = "1472"
TOTP_SECRET = "7S5OYFTQDYF5ZJDL2SGBCPYJX4"

# Initialize SmartConnect
obj = SmartConnect(api_key=API_KEY)

def login_to_angel():
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()
        data = obj.generateSession(CLIENT_CODE, PIN, totp)
        if data['status']:
            print("Login Successful!")
            return data['data']['jwtToken']
        else:
            print("Login Failed:", data['message'])
    except Exception as e:
        print("Login Error:", e)
    return None

def fetch_live_data():
    """Fetch 1-minute historical/intraday candles from Angel One for MCX Natural Gas"""
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "exchange": "MCX",
            "symboltoken": "543207",  # MCX Natural Gas token number
            "interval": "ONE_MINUTE",
            "fromdate": "2026-09-04 09:00",
            "todate": "2026-09-04 21:38"
        }
        
        response = obj.getCandleData(params)
        
        if response and response.get('status') and response.get('data'):
            raw_data = response['data']
            df = pd.DataFrame(raw_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            return df
    except Exception as e:
        print("Data fetch error:", e)
    
    return pd.DataFrame()

def calculate_vwap(df):
    """Calculate VWAP (Volume Weighted Average Price)"""
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    v_tp = typical_price * df['volume']
    cumulative_v_tp = v_tp.cumsum()
    cumulative_volume = df['volume'].cumsum()
    return cumulative_v_tp / cumulative_volume

def check_strategy():
    """Run VWAP and ORB strategy logic"""
    df = fetch_live_data()
    
    if df.empty or len(df) < 15:
        return "WAIT: Gathering data..."
        
    df['vwap'] = calculate_vwap(df)
    
    # Calculate ORB levels (First 15 minutes of the session)
    orb_high = df['high'].iloc[0:15].max()
    orb_low = df['low'].iloc[0:15].min()
    
    current_close = df['close'].iloc[-1]
    current_vwap = df['vwap'].iloc[-1]
    
    if current_close > orb_high and current_close > current_vwap:
        return "BUY_SIGNAL"
    elif current_close < orb_low and current_close < current_vwap:
        return "SELL_SIGNAL"
        
    return "NO_SIGNAL"

if __name__ == "__main__":
    jwt_token = login_to_angel()
    
    if jwt_token:
        print("VWAP + ORB Signal Bot started for Angel One...")
        while True:
            signal = check_strategy()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {signal}")
            time.sleep(60)  # Check every 1 minute
    else:
        print("Authentication failed. Check credentials.")