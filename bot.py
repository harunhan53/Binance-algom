import json
from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# .env'den API key'leri ve webhook şifresi alınıyor
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

client = Client(API_KEY, API_SECRET)

symbol = "BTCUSDT"

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

        # Webhook şifresi .env dosyasından çekiliyor
        if password != WEBHOOK_SECRET:
            return "Unauthorized", 401

        if signal == "BUY_40" and not position_open:
            try:
                client.create_order(
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
                client.create_order(
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
                client.create_order(
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
                client.create_order(
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
                qty = float(client.get_asset_balance(asset="BTC")["free"])
                if qty > 0:
                    client.create_order(
                        symbol=symbol,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_MARKET,
                        quantity=qty
                    )
                position_open = False
                alim40 = False
                alim60 = False
                print("STOP LOSS - tüm pozisyon kapatıldı.")
            except Exception as e:
                print(f"STOP hatası: {e}")

        elif signal == "TREND_BITTI" and position_open:
            try:
                qty = float(client.get_asset_balance(asset="BTC")["free"])
                if qty > 0:
                    client.create_order(
                        symbol=symbol,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_MARKET,
                        quantity=qty
                    )
                position_open = False
                alim40 = False
                alim60 = False
                print("TREND BİTTİ - tüm pozisyon kapatıldı.")
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
