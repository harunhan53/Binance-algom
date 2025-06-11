import os
import time
from binance.client import Client

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

client = Client(api_key, api_secret)

symbol = "BTCUSDT"

def check_signal():
    try:
        with open("signal.txt", "r") as file:
            return file.read().strip()
    except:
        return ""

def place_order(signal):
    quantity = 0.001  # küçük başla, test için
    if signal == "buy":
        order = client.order_market_buy(symbol=symbol, quantity=quantity)
        print("Buy order placed:", order)
    elif signal == "sell":
        order = client.order_market_sell(symbol=symbol, quantity=quantity)
        print("Sell order placed:", order)

while True:
    signal = check_signal()
    if signal in ["buy", "sell"]:
        place_order(signal)
        with open("signal.txt", "w") as file:
            file.write("")  # sinyal sıfırla
    time.sleep(5)
