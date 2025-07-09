from stock_universe import get_nifty_50_stocks
from kite_api import get_historical_data, place_order, get_ltp
from strategy_engine_v2 import should_enter_trade
from performance_logger import log_trade
from state_manager import is_bot_running
from risk_engine import within_risk_limits, update_daily_pnl
import time

CAPITAL = float(os.getenv("WALLET_CAPITAL", 1000))
MAX_LOSS = float(os.getenv("MAX_LOSS", 200))
MAX_PROFIT = float(os.getenv("MAX_PROFIT", 300))
RISK_PER_TRADE = 0.01  # 1%

def calculate_position_size(price):
    risk_amount = CAPITAL * RISK_PER_TRADE
    stop_loss = price * 0.01  # 1% SL
    qty = int(risk_amount / stop_loss)
    return max(1, qty)

def main():
    print("📈 Starting Trident Trade Bot...")

    while True:
        if not is_bot_running():
            print("⏸️ Bot is paused. Sleeping for 60s...")
            time.sleep(60)
            continue

        symbols = get_nifty_50_stocks()
        for symbol in symbols:
            try:
                ltp = get_ltp(symbol)
                historical_data = get_historical_data(symbol)

                signal, reason = should_enter_trade(historical_data)
                if signal:
                    if not within_risk_limits():
                        print("🛑 Risk limit reached. Halting trades.")
                        break

                    qty = calculate_position_size(ltp)
                    sl = round(ltp * 0.99, 2)  # 1% SL
                    tp = round(ltp * 1.015, 2)  # 1.5% Target

                    order = place_order(symbol=symbol, qty=qty, order_type="BUY")
                    print(f"✅ Order Placed: {symbol} @ ₹{ltp}, Qty: {qty}, SL: ₹{sl}, Target: ₹{tp}")

                    log_trade(symbol, ltp, sl, tp, qty, reason)
                    update_daily_pnl(ltp, sl, tp)

                    time.sleep(2)

            except Exception as e:
                print(f"⚠️ Error processing {symbol}: {e}")

        time.sleep(60)

if __name__ == "__main__":
    main()
