from utils import get_candles, calculate_ema, calculate_rsi, calculate_macd
from context_engine import detect_market_context

# Strategy: Buy if majority of indicators align with trend
# - EMA crossover (short > long)
# - RSI < 60 and rising
# - MACD above signal line
# - Nifty trend must support direction

MIN_CONDITIONS = 4

def evaluate_stock_v2(symbol):
    try:
        df = get_candles(symbol, interval="5minute", days=2)
        if df is None or df.empty or len(df) < 50:
            return "hold", "Insufficient data"

        df["EMA20"] = calculate_ema(df, 20)
        df["EMA50"] = calculate_ema(df, 50)
        df["RSI"] = calculate_rsi(df)
        df["MACD"], df["SIGNAL"] = calculate_macd(df)

        latest = df.iloc[-1]
        context = detect_market_context()

        conditions = 0
        reasons = []

        # EMA Crossover
        if latest["EMA20"] > latest["EMA50"]:
            conditions += 1
            reasons.append("EMA20 > EMA50")

        # RSI Logic
        if latest["RSI"] < 60 and df["RSI"].iloc[-1] > df["RSI"].iloc[-2]:
            conditions += 1
            reasons.append("RSI rising")

        # MACD > Signal Line
        if latest["MACD"] > latest["SIGNAL"]:
            conditions += 1
            reasons.append("MACD > Signal")

        # Market Context
        if context == "bullish":
            conditions += 1
            reasons.append("Bullish market context")

        if conditions >= MIN_CONDITIONS:
            reason = ", ".join(reasons)
            return "buy", reason
        else:
            return "hold", "Not enough confirmations"

    except Exception as e:
        return "error", str(e)
