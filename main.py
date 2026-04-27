from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Backforge API is Live", "message": "Engine Ready"}

@app.get("/get-data")
def get_stock_data(symbol: str, period: str = "1y"):
    try:
        ticker_symbol = symbol if "." in symbol else f"{symbol}.NS"
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return {"error": "No data found"}
        
        # Manual RSI Calculation (No pandas_ta needed)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        data = {
            "symbol": ticker_symbol,
            "dates": df.index.strftime('%Y-%m-%d').tolist(),
            "close": df['Close'].round(2).tolist(),
            "rsi": df['RSI'].fillna(50).round(2).tolist(),
            "volume": df['Volume'].tolist()
        }
        return data
    except Exception as e:
        return {"error": str(e)}