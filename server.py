from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_30a")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Server is running", 200

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload)

@app.route("/webhook", methods=["POST"])
def webhook():

    # First try JSON
    data = request.get_json(silent=True)

    # If not JSON, fallback to raw body
    if data is None:
        raw = request.data.decode("utf-8")
        data = {"signal": raw}

    signal = data.get("signal", "UNKNOWN")

    if signal == "TEST_BUY":
        send_telegram_message("<b>BUY SIGNAL</b>\nEntry: 100.5\nTarget: 102.5\nStoploss: 99.2")

    elif signal == "TEST_SELL":
        send_telegram_message("<b>SELL SIGNAL</b>\nEntry: 100.5\nTarget: 98.2\nStoploss: 101.1")

    else:
        send_telegram_message(f"Unknown Signal Received:\n{data}")

    return "OK", 200

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
