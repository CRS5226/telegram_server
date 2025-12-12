from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_30a")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

# Test homepage
@app.route("/", methods=["GET"])
def home():
    return "Server is running", 200

# Send Telegram message
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    requests.post(url, data=payload)

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():

    # Accept ANY data format (JSON or raw)
    raw = request.get_data(as_text=True)

    # Expected format: "143.25,TEST_BUY"
    parts = raw.split(",")

    if len(parts) < 2:
        send_telegram_message(f"Invalid payload received: {raw}")
        return "Invalid", 400

    price = float(parts[0])
    signal = parts[1].strip()

    # ATR placeholder for testing — replace later with real formula
    atr = 1.5

    entry = price

    if signal == "TEST_BUY":
        sl = entry - atr
        tp = entry + 2 * atr
        send_telegram_message(
            f"<b>BUY SIGNAL</b>\nEntry: {entry}\nTarget: {tp}\nStoploss: {sl}"
        )

    elif signal == "TEST_SELL":
        sl = entry + atr
        tp = entry - 2 * atr
        send_telegram_message(
            f"<b>SELL SIGNAL</b>\nEntry: {entry}\nTarget: {tp}\nStoploss: {sl}"
        )

    else:
        send_telegram_message(f"Unknown Signal Received:\n{raw}")

    return "OK", 200

# Run server on VPS
if __name__ == "__main__":
    try:
        public_ip = requests.get("https://api.ipify.org").text
    except:
        public_ip = "UNKNOWN"

    print("\n==============================")
    print(" Public IP:", public_ip)
    print(" Webhook URL: http://" + public_ip + ":5000/webhook")
    print("==============================\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
