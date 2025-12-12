from fastapi import FastAPI, Request, BackgroundTasks
import requests
import yfinance as yf
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_30a")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SYMBOL = "RELIANCE.NS"  # change for your testing

app = FastAPI()


# ==============================
# Send Telegram Message (async ready)
# ==============================
def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}

    # Non-blocking fast API call
    try:
        requests.post(url, data=payload, timeout=2)
    except:
        pass


# ==============================
# FAST Yahoo Live Price
# ==============================
def get_live_price():
    try:
        data = yf.download(SYMBOL, period="1d", interval="1m", progress=False)
        return float(data["Close"].iloc[-1])
    except:
        return 0.0


# ==============================
# HOME
# ==============================
@app.get("/")
def home():
    return {"status": "Server is running"}


# ==============================
# WEBHOOK (non-blocking)
# ==============================
@app.post("/webhook")
async def webhook(request: Request, background: BackgroundTasks):

    body = await request.body()
    signal = body.decode("utf-8").strip().upper()

    # Fetch price fast (sync but lightweight)
    price = get_live_price()
    atr = 1.5
    entry = price

    if signal == "TEST_BUY":
        sl = entry - atr
        tp = entry + 2 * atr
        msg = f"<b>BUY SIGNAL</b>\nEntry: {entry}\nTarget: {tp}\nStoploss: {sl}"
        background.add_task(send_telegram_message, msg)

    elif signal == "TEST_SELL":
        sl = entry + atr
        tp = entry - 2 * atr
        msg = f"<b>SELL SIGNAL</b>\nEntry: {entry}\nTarget: {tp}\nStoploss: {sl}"
        background.add_task(send_telegram_message, msg)

    else:
        background.add_task(send_telegram_message, f"Unknown: {signal}")

    return {"status": "ok"}


# ==============================
# SERVER STARTUP WITH PUBLIC IP PRINT
# ==============================
if __name__ == "__main__":
    public_ip = requests.get("https://api.ipify.org").text
    print("\n==============================")
    print(" Public IP:", public_ip)
    print(" Webhook URL: http://" + public_ip + ":5000/webhook")
    print("==============================\n")

    uvicorn.run(app, host="0.0.0.0", port=5000)
