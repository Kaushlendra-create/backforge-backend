from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

# 1. CORS Setup - Taaki aapka frontend backend se connect ho sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Backforge API is Live", "engine": "Ready"}

@app.get("/get-data")
def get_stock_data(symbol: str, period: str = "1y"):
    try:
        # 2. Symbol Format Logic
        symbol = symbol.upper().strip()
        
        # Agar symbol mein '.' (Stocks) ya '=' (Forex) ya '^' (Index) nahi hai, 
        # toh default Indian NSE stock (.NS) maan lo.
        if "." not in symbol and "=" not in symbol and "^" not in symbol:
            ticker_symbol = f"{symbol}.NS"
        else:
            ticker_symbol = symbol
        
        # 3. Fetching Data from Yahoo Finance
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return {"error": f"No data found for {ticker_symbol}. Check the symbol format."}
        
        # 4. RSI Calculation (Manual - No extra library needed)
        window = 14
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window, min_periods=1).mean()
        
        rs = gain / loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs))
        df['RSI'] = df['RSI'].fillna(50) # Missing values ko 50 kar do

        # 5. Data Cleaning (Inf/NaN values hatao taaki JSON crash na ho)
        clean_close = df['Close'].replace([np.inf, -np.inf], 0).round(2).tolist()
        clean_rsi = df['RSI'].replace([np.inf, -np.inf], 50).round(2).tolist()
        dates = df.index.strftime('%Y-%m-%d').tolist()

        return {
            "symbol": ticker_symbol,
            "dates": dates,
            "close": clean_close,
            "rsi": clean_rsi,
            "count": len(dates)
        }

    except Exception as e:
        # 6. Detailed Error Reporting
        return {"error": str(e), "status": "failed"}