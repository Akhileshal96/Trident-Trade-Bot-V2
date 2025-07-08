from utils import calculate_ema, calculate_rsi, calculate_macd, get_candles
from kite_api import kite

# Adaptive Strategy Parameters
EMA_FAST = 5
EMA_SLOW = 20
RSI_PERIOD = 14

BREAKOUT_RSI_RANGE = (55, 70)
REVERSAL_RSI_THRESHOLD = 30

TP_BREAKOUT = 0.03
SL_BREAKOUT = 0.015
TP_REVERSAL = 0.02
SL_REVERSAL = 0.012

def detect_market_context():
    nifty_candles = get_candles("NIFTY 50", interval="5minute", days=2)
    nifty_candles["EMA20"] = calculate_ema(nifty_candles, 20)
    nifty_candles["EMA50"] = calculate_ema(nifty_candles, 50)

    last = nifty_candles.iloc[-1]
    if last["EMA20"] > last["EMA50"]:
        return "bullish"
    else:
        return "bearish"

def evaluate_stock_v2(stock_symbol, context):
    df = get_candles(stock_symbol, interval="5minute", days=2)
    if len(df) < 30:
        return None

    df["EMA_FAST"] = calculate_ema(df, EMA_FAST)
    df["EMA_SLOW"] = calculate_ema(df, EMA_SLOW)
    df["RSI"] = calculate_rsi(df, RSI_PERIOD)
    df["MACD"], df["MACD_SIGNAL"] = calculate_macd(df)

    latest = df.iloc[-1]
    entry_price = kite.ltp(f"NSE:{stock_symbol}")[f"NSE:{stock_symbol}"]["last_price"]

    if context == "bullish":
        if (latest["EMA_FAST"] > latest["EMA_SLOW"] and
            BREAKOUT_RSI_RANGE[0] < latest["RSI"] < BREAKOUT_RSI_RANGE[1] and
            latest["MACD"] > latest["MACD_SIGNAL"]):

            sl = round(entry_price - entry_price * SL_BREAKOUT, 2)
            tp = round(entry_price + entry_price * TP_BREAKOUT, 2)
            return build_trade_object(stock_symbol, entry_price, sl, tp, "breakout")

    elif context == "bearish":
        if (latest["RSI"] < REVERSAL_RSI_THRESHOLD and
            latest["MACD"] > latest["MACD_SIGNAL"]):

            sl = round(entry_price - entry_price * SL_REVERSAL, 2)
            tp = round(entry_price + entry_price * TP_REVERSAL, 2)
            return build_trade_object(stock_symbol, entry_price, sl, tp, "reversal")

    return None

def build_trade_object(symbol, entry, sl, tp, mode):
    qty = max(int(1000 // entry), 1)
    return {
        "symbol": symbol,
        "entry_price": entry,
        "stop_loss": sl,
        "target_price": tp,
        "qty": qty,
        "mode": mode
    }
