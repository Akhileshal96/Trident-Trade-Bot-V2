import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configurable via .env
MAX_PROFIT = float(os.getenv("MAX_PROFIT", 5000))
MAX_LOSS = float(os.getenv("MAX_LOSS", 2000))
WALLET_CAPITAL = float(os.getenv("WALLET_CAPITAL", 1000))

_bot_running = True
_daily_pnl = 0
trade_log = []

def can_trade():
    return _bot_running and abs(_daily_pnl) < MAX_LOSS and _daily_pnl < MAX_PROFIT

def stop_trading():
    global _bot_running
    _bot_running = False

def resume_trading():
    global _bot_running
    _bot_running = True

def update_pnl(pnl):
    global _daily_pnl
    _daily_pnl += pnl

def reset_daily_risk():
    global _daily_pnl
    _daily_pnl = 0
    trade_log.clear()

def log_trade(symbol, entry, exit, qty, pnl):
    record = {
        "symbol": symbol,
        "entry": entry,
        "exit": exit,
        "qty": qty,
        "pnl": pnl,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    trade_log.append(record)

    with open("trade_log.txt", "a") as f:
        f.write(f"{record['timestamp']} | {symbol} | Entry: ₹{entry} | Exit: ₹{exit} | Qty: {qty} | PnL: ₹{pnl}\n")

def set_max_profit(amount):
    global MAX_PROFIT
    MAX_PROFIT = amount

def set_max_loss(amount):
    global MAX_LOSS
    MAX_LOSS = amount

def set_wallet_capital(amount):
    global WALLET_CAPITAL
    WALLET_CAPITAL = amount
