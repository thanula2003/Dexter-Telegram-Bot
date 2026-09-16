import os
import requests

from flask import Flask, request
from dotenv import load_dotenv

from ai import ask_dexter
from limiter import can_use, setup_database


load_dotenv()


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing")


BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


app = Flask(__name__)


# Create the database table if it doesn't exist
setup_database()


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


@app.route("/", methods=["GET"])
def home():

    return "Dexter is running."


@app.route("/telegram", methods=["POST"])
def telegram_webhook():

    update = request.get_json()

    if not update:
        return "OK"


    message = update.get("message")

    if not message:
        return "OK"


    chat_id = message["chat"]["id"]

    text = message.get("text", "").strip()

    if not text:
        return "OK"


    # -------------------------
    # /start
    # -------------------------

    if text == "/start":

        send_message(
            chat_id,
            "Hello! I'm Dexter. 🤖\n\n"
            "I'm an IT-focused AI assistant.\n"
            "Ask me anything about programming, "
            "databases, networking, cybersecurity, "
            "AI, or other IT topics."
        )

        return "OK"


    # -------------------------
    # /help
    # -------------------------

    if text == "/help":

        send_message(
            chat_id,
            "I'm Dexter, an IT-focused AI assistant.\n\n"
            "I can help you with:\n"
            "• Programming\n"
            "• Web development\n"
            "• Databases\n"
            "• Networking\n"
            "• Cybersecurity\n"
            "• AI & Machine Learning\n"
            "• Operating Systems\n"
            "• APIs\n"
            "• Git & GitHub\n"
            "• Data Structures\n\n"
            "You can send up to 8 messages per day."
        )

        return "OK"


    # -------------------------
    # Daily limit
    # -------------------------

    if not can_use(chat_id):

        send_message(
            chat_id,
            "You've reached your 8-message limit for today. "
            "Your limit will reset tomorrow."
        )

        return "OK"


    # -------------------------
    # Ask Dexter
    # -------------------------

    try:

        answer = ask_dexter(text)

        send_message(chat_id, answer)

    except Exception as error:

        print("Error:", error)

        send_message(
            chat_id,
            "Sorry, I couldn't process your question right now. "
            "Please try again later."
        )


    return "OK"


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )