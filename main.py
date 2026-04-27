from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

app = FastAPI()

# Frontend (Netlify) ko access dene ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Backforge API is Live", "message": "Ready for backtesting"}

@app.get("/get-data")
def get_stock_data(symbol: str, period: str = "1y"):
    try:
        # NSE stocks ke liye suffix handle karna
        ticker_symbol = symbol if "." in symbol else f"{symbol}.NS"
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return {"error": "No data found for this symbol"}
        
        data = {
            "symbol": ticker_symbol,
            "dates": df.index.strftime('%Y-%m-%d').tolist(),
            "close": df['Close'].round(2).tolist(),
            "high": df['High'].round(2).tolist(),
            "low": df['Low'].round(2).tolist(),
            "volume": df['Volume'].tolist()
        }
        return data
    except Exception as e:
        return {"error": str(e)}