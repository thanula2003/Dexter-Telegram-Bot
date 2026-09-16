import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing")

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"

response = requests.post(
    url,
    data={
        "url": "https://dexter-telegram-app.onrender.com/telegram"
    },
    timeout=30
)

print(response.json())