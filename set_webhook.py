import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

RENDER_URL = "https://dexter-telegram-app.onrender.com/telegram"

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"

response = requests.post(
    url,
    data={"url": RENDER_URL},
    timeout=30
)

print(response.json())