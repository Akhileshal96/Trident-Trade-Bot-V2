import asyncio
from strategy_engine_v2 import evaluate_stock_v2
from stock_universe import fetch_nse_symbols
from utils import get_candles
from kite_api import kite
from risk_engine import can_trade, log_trade, update_pnl
from telegram_bot import notify_trade_entry, notify_exit
import time

TRADE_INTERVAL = 300  # seconds (5 minutes)
TARGET_PERCENT = 1.5  # Target profit percent
STOPLOSS_PERCENT = 1.0  # Stop-loss percent

async def run_trading_loop():
    print("✅ Trident Bot Live Trading Started")

    while True:
        if not can_trade():
            print("⏸️ Trading paused due to risk limits.")
            await asyncio.sleep(TRADE_INTERVAL)
            continue

        symbols = fetch_nse_symbols("NIFTY 50")
        for symbol in symbols:
            print(f"🔍 Checking {symbol}...")
            decision, reason = evaluate_stock_v2(symbol)

            if decision == "buy":
                try:
                    ltp = kite.ltp(f"NSE:{symbol}")[f"NSE:{symbol}"]["last_price"]
                    sl_price = round(ltp * (1 - STOPLOSS_PERCENT / 100), 2)
                    tp_price = round(ltp * (1 + TARGET_PERCENT / 100), 2)
                    qty = 1  # Later: make dynamic based on capital and SL risk

                    order_id = kite.place_order(
                        variety=kite.VARIETY_REGULAR,
                        exchange=kite.EXCHANGE_NSE,
                        tradingsymbol=symbol,
                        transaction_type=kite.TRANSACTION_TYPE_BUY,
                        quantity=qty,
                        product=kite.PRODUCT_MIS,
                        order_type=kite.ORDER_TYPE_MARKET
                    )

                    await notify_trade_entry(symbol, ltp, sl_price, tp_price, qty, reason)
                    print(f"✅ Buy order placed: {symbol} @ ₹{ltp}")

                    # Monitor for SL or TP hit (exit simulation)
                    exited = False
                    while not exited:
                        new_ltp = kite.ltp(f"NSE:{symbol}")[f"NSE:{symbol}"]["last_price"]
                        if new_ltp >= tp_price:
                            pnl = (tp_price - ltp) * qty
                            await notify_exit(symbol, tp_price, pnl)
                            log_trade(symbol, ltp, tp_price, qty, pnl)
                            update_pnl(pnl)
                            exited = True
                        elif new_ltp <= sl_price:
                            pnl = (sl_price - ltp) * qty
                            await notify_exit(symbol, sl_price, pnl)
                            log_trade(symbol, ltp, sl_price, qty, pnl)
                            update_pnl(pnl)
                            exited = True
                        await asyncio.sleep(15)

                except Exception as e:
                    print(f"❌ Error while placing order for {symbol}: {e}")

        await asyncio.sleep(TRADE_INTERVAL)

if __name__ == '__main__':
    asyncio.run(run_trading_loop())
