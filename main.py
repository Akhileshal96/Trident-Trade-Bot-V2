import asyncio
import time
from strategy_engine_v2 import evaluate_stock_v2
from context_engine import detect_market_context
from risk_engine import can_trade, update_pnl, log_trade, trade_log, reset_daily_risk
from telegram_bot import notify_trade_entry, notify_exit, notify_daily_summary
from stock_universe import fetch_nse_symbols

STOCK_LIST = fetch_nse_symbols("NIFTY 50")  # Live fetch from NSE
INTERVAL = 300  # 5 minutes

async def execute_trade_loop():
    while True:
        if not can_trade():
            await asyncio.sleep(INTERVAL)
            continue

        context = detect_market_context()
        print(f"Market context: {context}")

        for stock in STOCK_LIST:
            try:
                stock_data = evaluate_stock_v2(stock, context)
                if stock_data:
                    entry = stock_data['entry_price']
                    sl = stock_data['stop_loss']
                    tp = stock_data['target_price']
                    qty = stock_data['qty']
                    symbol = stock_data['symbol']
                    mode = stock_data['mode']

                    await notify_trade_entry(symbol, entry, sl, tp, qty, f"{mode.upper()} Strategy")

                    exit_price = tp
                    pnl = round((exit_price - entry) * qty, 2)

                    log_trade(symbol, entry, exit_price, qty, pnl)
                    update_pnl(pnl)
                    await notify_exit(symbol, exit_price, pnl)

                    time.sleep(2)
            except Exception as e:
                print(f"Error with {stock}: {e}")

        await asyncio.sleep(INTERVAL)

async def daily_summary():
    await notify_daily_summary(trade_log)
    reset_daily_risk()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(execute_trade_loop())
        loop.run_forever()
    except KeyboardInterrupt:
        print("Bot stopped by user.")
