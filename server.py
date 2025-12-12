from flask import Flask, request
import requests
import os
import yfinance as yf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_30a")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# SYMBOL to fetch in real-time (you can later pass symbol through webhook)
SYMBOL = "RELIANCE.NS"   # CHANGE THIS TO YOUR STOCK

app = Flask(__name__)

# Homepage
@app.route("/", methods=["GET"])
def home():
    return "Server is running", 200

# Telegram sender
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

# Fetch live 1-minute candle price
def get_live_price():
    ticker = yf.Ticker(SYMBOL)
    data = ticker.history(period="1d", interval="1m")  # CORRECT FORMAT

    if data.empty:
        raise Exception("No live data received from YFinance!")

    return float(data["Close"].iloc[-1])

# Webhook
@app.route("/webhook", methods=["POST"])
def webhook():

    raw = request.get_data(as_text=True).strip()
    signal = raw.upper()  # Example: "TEST_BUY"

    try:
        price = get_live_price()
    except Exception as e:
        send_telegram_message(f"Error fetching price: {str(e)}")
        return "Price error", 500

    # Placeholder ATR for now — we can compute real ATR later
    atr = 1.5
    entry = price

    if signal == "TEST_BUY":
        sl = entry - atr
        tp = entry + (2 * atr)
        send_telegram_message(
            f"<b>BUY SIGNAL</b>\nEntry: {entry}\nTarget: {tp}\nStoploss: {sl}"
        )

    elif signal == "TEST_SELL":
        sl = entry + atr
        tp = entry - (2 * atr)
        send_telegram_message(
            f"<b>SELL SIGNAL</b>\nEntry: {entry}\nTarget: {tp}\nStoploss: {sl}"
        )

    else:
        send_telegram_message(f"Unknown Payload Received:\n{raw}")

    return "OK", 200

# Run server publicly
if __name__ == "__main__":
    public_ip = requests.get("https://api.ipify.org").text

    print("\n==============================")
    print(" Public IP:", public_ip)
    print(" Webhook URL: http://" + public_ip + ":5000/webhook")
    print("==============================\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
