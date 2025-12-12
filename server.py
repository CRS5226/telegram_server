from fastapi import FastAPI, Request, BackgroundTasks
import requests
import yfinance as yf
import os
from datetime import datetime
from dotenv import load_dotenv
import uvicorn

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_30a")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SYMBOL = "RELIANCE.NS"  # You can change this for testing

app = FastAPI()


# ============================================
# Send Telegram Message (Non-blocking)
# ============================================
def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=2)
    except:
        pass


# ============================================
# FAST Yahoo Live Price
# ============================================
def get_live_price():
    try:
        data = yf.download(SYMBOL, period="1d", interval="1m", progress=False)
        return float(data["Close"].iloc[-1])
    except:
        return 0.0


# ============================================
# HOME CHECK
# ============================================
@app.get("/")
def home():
    return {"status": "Server is running"}


# ============================================
# WEBHOOK (NON-BLOCKING)
# ============================================
@app.post("/webhook")
async def webhook(request: Request, background: BackgroundTasks):

    body = (await request.body()).decode("utf-8").strip().upper()

    # LIVE MARKET PRICE
    price = get_live_price()

    # Our test logic: entry/target/stoploss offsets
    entry = price + 100
    target = price + 500
    stop = price - 100

    # Percentage differences
    target_diff = ((target - entry) / entry) * 100
    stop_diff = ((entry - stop) / entry) * 100

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timeframe = "30min"

    # ==========================
    # Handle BUY / SELL Signals
    # ==========================
    if body == "BUY":
        msg = (
            f"🚀 *BUY SIGNAL*\n"
            f"Symbol: `{SYMBOL}`\n"
            f"Timeframe: `{timeframe}`\n"
            f"Timestamp: `{timestamp}`\n"
            f"Live Price: `{price}`\n\n"
            f"🎯 Entry: `{entry}` | Target: `{target}` | Stoploss: `{stop}`\n"
            f"📈 Target Diff: `{target_diff:.2f}%`\n"
            f"📉 Stoploss Diff: `{stop_diff:.2f}%`"
        )
        background.add_task(send_telegram_message, msg)

    elif body == "SELL":
        msg = (
            f"🔻 *SELL SIGNAL*\n"
            f"Symbol: `{SYMBOL}`\n"
            f"Timeframe: `{timeframe}`\n"
            f"Timestamp: `{timestamp}`\n"
            f"Live Price: `{price}`\n\n"
            f"🎯 Entry: `{entry}` | Target: `{target}` | Stoploss: `{stop}`\n"
            f"📈 Target Diff: `{target_diff:.2f}%`\n"
            f"📉 Stoploss Diff: `{stop_diff:.2f}%`"
        )
        background.add_task(send_telegram_message, msg)

    else:
        background.add_task(send_telegram_message, f"`Unknown` signal received: {body}")

    return {"status": "ok"}


# ============================================
# SERVER STARTUP
# ============================================
if __name__ == "__main__":
    public_ip = requests.get("https://api.ipify.org").text
    print("\n==============================")
    print(" Public IP:", public_ip)
    print(" Webhook URL: http://" + public_ip + ":5000/webhook")
    print("==============================\n")

    uvicorn.run(app, host="0.0.0.0", port=5000)
