import os
import math
from flask import Flask, request
from binance.client import Client
from binance.enums import *
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = Client(API_KEY, API_SECRET)

symbol = "BTCUSDT"
position_open = False
alim40 = False
alim60 = False

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Telegram gönderim hatası: {e}")

@app.route('/webhook-gizli-path', methods=['POST'])
def webhook():
    global position_open, alim40, alim60
    try:
        signal = request.data.decode().strip()
        if not signal:
            return "Bad Request", 400

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
                msg = "✅ 40% ALIM gerçekleşti."
                print(msg)
                send_telegram_message(msg)
            except Exception as e:
                print(f"❌ BUY_40 hatası: {e}")
                send_telegram_message(f"❌ BUY_40 hatası: {e}")

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
                msg = "✅ 60% ALIM gerçekleşti."
                print(msg)
                send_telegram_message(msg)
            except Exception as e:
                print(f"❌ BUY_60 hatası: {e}")
                send_telegram_message(f"❌ BUY_60 hatası: {e}")

        elif signal == "SELL_40" and alim40:
            try:
                balance = client.get_asset_balance(asset="BTC")
                qty = float(balance["free"])
                qty = math.floor(qty * 1e5) / 1e5
                client.create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=qty
                )
                alim40 = False
                if not alim60:
                    position_open = False
                msg = "✅ 40% SATIM gerçekleşti."
                print(msg)
                send_telegram_message(msg)
            except Exception as e:
                print(f"❌ SELL_40 hatası: {e}")
                send_telegram_message(f"❌ SELL_40 hatası: {e}")

        elif signal == "SELL_60" and alim60:
            try:
                balance = client.get_asset_balance(asset="BTC")
                qty = float(balance["free"])
                qty = math.floor(qty * 1e5) / 1e5
                client.create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=qty
                )
                alim60 = False
                if not alim40:
                    position_open = False
                msg = "✅ 60% SATIM gerçekleşti."
                print(msg)
                send_telegram_message(msg)
            except Exception as e:
                print(f"❌ SELL_60 hatası: {e}")
                send_telegram_message(f"❌ SELL_60 hatası: {e}")

        elif signal in ["STOP", "TREND_BITTI"] and position_open:
            try:
                balance = client.get_asset_balance(asset="BTC")
                qty = float(balance["free"])
                qty = math.floor(qty * 1e5) / 1e5
                if qty > 0:
                    client.create_order(
                        symbol=symbol,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_MARKET,
                        quantity=qty
                    )
                    msg = f"✅ {signal} - tüm BTC satıldı."
                    print(msg)
                    send_telegram_message(msg)
                position_open = False
                alim40 = False
                alim60 = False
            except Exception as e:
                print(f"❌ {signal} hatası: {e}")
                send_telegram_message(f"❌ {signal} hatası: {e}")

        elif signal == "REENTRY_ALLOWED":
            alim40 = False
            alim60 = False
            position_open = False
            msg = "🔄 Tekrar alım izni verildi - bayraklar sıfırlandı."
            print(msg)
            send_telegram_message(msg)

        return "OK"

    except Exception as e:
        print(f"🔥 Genel webhook hatası: {e}")
        send_telegram_message(f"🔥 Genel webhook hatası: {e}")
        return "HATA", 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
