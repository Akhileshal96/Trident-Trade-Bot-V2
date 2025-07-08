import os
from dotenv import load_dotenv
from kiteconnect import KiteConnect

load_dotenv()

KITE_API_KEY = os.getenv("KITE_API_KEY")
ZERODHA_ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=KITE_API_KEY)
kite.set_access_token(ZERODHA_ACCESS_TOKEN)
