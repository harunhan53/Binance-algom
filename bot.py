import json
from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os

app = Flask(__name__)

# Binance API key'leri environment'tan alınıyor
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

# İşlem yapılacak sembol
symbol = "BTCUSDT"

# Pozisyon durumu takip değişkeni
position_open = False
alim40 = False
alim60 = False

@app.route('/webhook-gizli-path', methods=['POST'])
def webhook():
    global position_open, alim40, alim60

    data = json.loads(request.data)
    signal = data.get("alert")
    password = data.get("password")

    # Şifre kontrolü
    if password != "z0naL2025":
        return "Unauthorized", 403

    if signal == "BUY_40" and not position_open:
        try:
            usdt_balance = float(client.get_asset_balance(asset="USDT")["free"])
            amount_to_spend = usdt_balance * 0.4
            btc_price = float(client.get_symbol_ticker(symbol=symbol)["price"])
            quantity = round(amount_to_spend / btc_price, 6)

            order = client.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            alim40 = True
            position_open = True
            print("40% ALIM gerçekleşti.")
        except Exception as e:
            print(f"BUY_40 hatası: {e}")

    elif signal == "BUY_60" and not alim60:
        try:
            usdt_balance = float(client.get_asset_balance(asset="USDT")["free"])
            amount_to_spend = usdt_balance * 0.6
            btc_price = float(client.get_symbol_ticker(symbol=symbol)["price"])
            quantity = round(amount_to_spend / btc_price, 6)

            order = client.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            alim60 = True
            position_open = True
            print("60% ALIM gerçekleşti.")
        except Exception as e:
            print(f"BUY_60 hatası: {e}")

    elif signal == "SELL_40" and alim40:
        try:
            balance = float(client.get_asset_balance(asset="BTC")["free"])
            qty = round(balance * 0.4, 6)

            order = client.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
            alim40 = False
            if not alim60:
                position_open = False
            print("40% SATIM gerçekleşti.")
        except Exception as e:
            print(f"SELL_40 hatası: {e}")

    elif signal == "SELL_60" and alim60:
        try:
            balance = float(client.get_asset_balance(asset="BTC")["free"])
            qty = round(balance * 0.6, 6)

            order = client.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
            alim60 = False
            if not alim40:
                position_open = False
            print("60% SATIM gerçekleşti.")
        except Exception as e:
            print(f"SELL_60 hatası: {e}")

    elif signal == "STOP" and position_open:
        try:
            balance = float(client.get_asset_balance(asset="BTC")["free"])
            if balance > 0:
                client.create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=round(balance, 6)
                )
                print("STOP LOSS - tüm pozisyon kapatıldı.")
            position_open = False
            alim40 = False
            alim60 = False
        except Exception as e:
            print(f"STOP hatası: {e}")

    elif signal == "TREND_BITTI" and position_open:
        try:
            balance = float(client.get_asset_balance(asset="BTC")["free"])
            if balance > 0:
                client.create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=round(balance, 6)
                )
                print("TREND BİTTİ - tüm pozisyon kapatıldı.")
            position_open = False
            alim40 = False
            alim60 = False
        except Exception as e:
            print(f"TREND_BITTI hatası: {e}")

    return "OK"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
