from utils import get_candles, calculate_ema

def detect_market_context():
    """
    Determines the market trend using EMA crossover on NIFTY 50.
    Returns: 'bullish', 'bearish', or 'neutral'
    """
    df = get_candles("NIFTY 50", interval="5minute", days=2)
    if df is None or df.empty:
        return "neutral"

    df["EMA20"] = calculate_ema(df, 20)
    df["EMA50"] = calculate_ema(df, 50)

    latest = df.iloc[-1]
    if latest["EMA20"] > latest["EMA50"]:
        return "bullish"
    elif latest["EMA20"] < latest["EMA50"]:
        return "bearish"
    else:
        return "neutral"
