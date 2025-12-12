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


# Send message to Telegram
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
    data = request.json
    if not data:
        return "No JSON received", 400

    signal = data.get("signal", "UNKNOWN")

    if signal == "TEST_BUY":
        send_telegram_message(
            "<b>BUY SIGNAL</b>\nEntry: 100.5\nTarget: 102.5\nStoploss: 99.2"
        )

    elif signal == "TEST_SELL":
        send_telegram_message(
            "<b>SELL SIGNAL</b>\nEntry: 100.5\nTarget: 98.2\nStoploss: 101.1"
        )

    else:
        send_telegram_message(f"Unknown Signal Received:\n{data}")

    return "OK", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
