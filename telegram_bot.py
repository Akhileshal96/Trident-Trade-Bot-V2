from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
from risk_engine import can_trade, stop_trading, resume_trading, set_max_profit, set_max_loss, set_wallet_capital
from performance_logger import LOG_FILE
from kite_api_config import update_token_in_env

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_USERS = list(map(int, os.getenv("AUTHORIZED_USERS", "").split(",")))

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def send_message(text):
    for user_id in AUTHORIZED_USERS:
        try:
            await client.send_message(user_id, text)
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

# 📩 Trade Alerts
async def notify_trade_entry(symbol, price, sl, tp, qty, reason):
    msg = f"\n✅ BUY Alert: {symbol} @ ₹{price}\nSL: ₹{sl} | Target: ₹{tp} | Qty: {qty}\nReason: {reason}"
    await send_message(msg)

async def notify_exit(symbol, price, pnl):
    status = "🎯 TP Hit" if pnl > 0 else "❌ SL Hit"
    msg = f"\n{status} for {symbol}\nExit Price: ₹{price} | P&L: ₹{pnl}"
    await send_message(msg)

async def notify_daily_summary(summary):
    msg = "\n📊 Daily Summary:\n"
    for trade in summary:
        msg += f"{trade['symbol']}: P&L ₹{trade['pnl']}\n"
    net = sum([t['pnl'] for t in summary])
    msg += f"Net P&L: ₹{net}"
    await send_message(msg)

async def notify_custom(text):
    await send_message(text)

# 🔘 Bot Commands
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    if event.sender_id in AUTHORIZED_USERS:
        await event.respond("🤖 Trident Bot Online!\nUse /status, /stop, /resume, /log, /setprofit, /setloss, /setcapital, /token")

@client.on(events.NewMessage(pattern='/status'))
async def status_handler(event):
    if event.sender_id in AUTHORIZED_USERS:
        status = "✅ Running" if can_trade() else "⛔ Paused"
        await event.respond(f"Bot Status: {status}")

@client.on(events.NewMessage(pattern='/stop'))
async def stop_handler(event):
    if event.sender_id in AUTHORIZED_USERS:
        stop_trading()
        await event.respond("⛔ Trading paused manually.")

@client.on(events.NewMessage(pattern='/resume'))
async def resume_handler(event):
    if event.sender_id in AUTHORIZED_USERS:
        resume_trading()
        await event.respond("✅ Trading resumed.")

@client.on(events.NewMessage(pattern='/log'))
async def log_handler(event):
    if event.sender_id in AUTHORIZED_USERS:
        try:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()[-5:]
                response = "\n🧾 Last 5 Trades:\n" + "".join(lines)
        except Exception as e:
            response = f"Failed to read log: {e}"
        await event.respond(response)

@client.on(events.NewMessage(pattern='/setprofit (\\d+)'))
async def setprofit_handler(event):
    if event.sender_id in AUTHORIZED_USERS:
        amount = int(event.pattern_match.group(1))
        set_max_profit(amount)
        await event.respond(f"✅ Max Profit set to ₹{amount}")

@client.on(events.NewMessage(pattern='/setloss (\\d+)'))
async def setloss_handler(event):
    if event.sender_id in AUTHORIZED_USERS:
        amount = int(event.pattern_match.group(1))
        set_max_loss(amount)
        await event.respond(f"✅ Max Loss set to ₹{amount}")

@client.on(events.NewMessage(pattern='/setcapital (\\d+)'))
async def setcapital_handler(event):
    if event.sender_id in AUTHORIZED_USERS:
        amount = int(event.pattern_match.group(1))
        set_wallet_capital(amount)
        await event.respond(f"✅ Wallet Capital set to ₹{amount}")

@client.on(events.NewMessage(pattern='/token (.+)'))
async def token_update_handler(event):
    if event.sender_id in AUTHORIZED_USERS:
        new_token = event.pattern_match.group(1)
        try:
            update_token_in_env(new_token)
            await event.respond("✅ Zerodha token updated successfully.")
        except Exception as e:
            await event.respond(f"❌ Failed to update token: {e}")
