import os
import requests

from dotenv import load_dotenv
from ai import ask_dexter
from limiter import can_use


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing")


BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id, text):

    max_length = 4000

    parts = [
        text[i:i + max_length]
        for i in range(0, len(text), max_length)
    ]

    for part in parts:

        requests.post(
            f"{BASE_URL}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": part
            },
            timeout=30
        )


print("Dexter Telegram test is running...")
print("Send a message to your bot.")


offset = None


while True:

    response = requests.get(
        f"{BASE_URL}/getUpdates",
        params={
            "offset": offset,
            "timeout": 30
        },
        timeout=35
    )

    data = response.json()

    if not data.get("ok"):
        print("Telegram error:", data)
        continue


    for update in data["result"]:

        offset = update["update_id"] + 1

        message = update.get("message")

        if not message:
            continue

        chat_id = message["chat"]["id"]

        text = message.get("text", "").strip()

        if not text:
            continue


        print(f"Received: {text}")


        if text == "/start":

            send_message(
                chat_id,
                "Hello! I'm Dexter. 🤖\n\n"
                "I'm an IT-focused AI assistant.\n"
                "Ask me an IT question."
            )

            continue


        if text == "/help":

            send_message(
                chat_id,
                "I can help with programming, "
                "web development, databases, "
                "networking, cybersecurity, AI, "
                "APIs, Git, and other IT topics.\n\n"
                "You can ask 8 AI questions per day."
            )

            continue


        if not can_use(chat_id):

            send_message(
                chat_id,
                "You've reached your 8-question limit for today.\n"
                "Your limit will reset tomorrow."
            )

            continue


        try:

            answer = ask_dexter(text)

            send_message(chat_id, answer)

            print("Answer sent.")

        except Exception as error:

            print("AI error:", error)

            send_message(
                chat_id,
                "Sorry, I couldn't process that question."
            )