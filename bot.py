import json
from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Binance API key'leri environment'tan alınıyor
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

# İşlem yapılacak sembol
symbol = "BTCUSDT"

# Pozisyon durumu takip değişkenleri
position_open = False
alim40 = False
alim60 = False

@app.route('/webhook-gizli-path', methods=['POST'])
def webhook():
    global position_open, alim40, alim60

    try:
        data = json.loads(request.data)
        signal = data.get("alert")
        password = data.get("password")

        if password != "z0naL2025":
            return "Unauthorized", 401

        if signal == "BUY_40" and not position_open:
            try:
                order = client.create_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quoteOrderQty=40
                )
                alim40 = True
                position_open = True
                print("40% ALIM gerçekleşti.")
            except Exception as e:
                print(f"BUY_40 hatası: {e}")

        elif signal == "BUY_60" and not alim60:
            try:
                order = client.create_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quoteOrderQty=60
                )
                alim60 = True
                position_open = True
                print("60% ALIM gerçekleşti.")
            except Exception as e:
                print(f"BUY_60 hatası: {e}")

        elif signal == "SELL_40" and alim40:
            try:
                order = client.create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quoteOrderQty=40
                )
                alim40 = False
                if not alim60:
                    position_open = False
                print("40% SATIM gerçekleşti.")
            except Exception as e:
                print(f"SELL_40 hatası: {e}")

        elif signal == "SELL_60" and alim60:
            try:
                order = client.create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quoteOrderQty=60
                )
                alim60 = False
                if not alim40:
                    position_open = False
                print("60% SATIM gerçekleşti.")
            except Exception as e:
                print(f"SELL_60 hatası: {e}")

        elif signal == "STOP" and position_open:
            try:
                balance = client.get_asset_balance(asset="BTC")
                qty = float(balance["free"])
                if qty > 0:
                    client.create_order(
                        symbol=symbol,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_MARKET,
                        quantity=qty
                    )
                    print("STOP LOSS - tüm pozisyon kapatıldı.")
                position_open = False
                alim40 = False
                alim60 = False
            except Exception as e:
                print(f"STOP hatası: {e}")

        elif signal == "TREND_BITTI" and position_open:
            try:
                balance = client.get_asset_balance(asset="BTC")
                qty = float(balance["free"])
                if qty > 0:
                    client.create_order(
                        symbol=symbol,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_MARKET,
                        quantity=qty
                    )
                    print("TREND BİTTİ - tüm pozisyon kapatıldı.")
                position_open = False
                alim40 = False
                alim60 = False
            except Exception as e:
                print(f"TREND_BITTI hatası: {e}")

        elif signal == "REENTRY_ALLOWED":
            alim40 = False
            alim60 = False
            position_open = False
            print("Tekrar alım izni verildi - bayraklar sıfırlandı.")

        return "OK"

    except Exception as e:
        print(f"Genel webhook hatası: {e}")
        return "HATA", 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
