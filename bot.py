import os
import requests

from flask import Flask, request
from dotenv import load_dotenv

from ai import ask_dexter, ask_dexter_with_image
from limiter import can_use, setup_database

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# Create database table if it doesn't exist
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


def download_telegram_file(file_id):

    # Get Telegram file information
    response = requests.get(
        f"{BASE_URL}/getFile",
        params={"file_id": file_id},
        timeout=30
    )

    response.raise_for_status()

    file_data = response.json()

    if not file_data.get("ok"):
        raise Exception("Could not get Telegram file information")

    file_path = file_data["result"]["file_path"]

    # Download actual image
    file_url = (
        f"https://api.telegram.org/file/bot"
        f"{TOKEN}/{file_path}"
    )

    image_response = requests.get(
        file_url,
        timeout=30
    )

    image_response.raise_for_status()

    return image_response.content


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

    # --------------------------------
    # TEXT MESSAGE
    # --------------------------------

    text = message.get("text", "").strip()

    # --------------------------------
    # /start
    # --------------------------------

    if text == "/start":

        send_message(
            chat_id,
            "Hey, I'm Dexter. 👋\n\n"
            "Your IT-focused AI buddy.\n\n"
            "I can help you with:\n"
            "• Programming\n"
            "• Web development\n"
            "• Databases\n"
            "• APIs\n"
            "• Cybersecurity\n"
            "• AI & Machine Learning\n"
            "• Git & GitHub\n"
            "• Networking\n"
            "• Data Structures\n\n"
            "Ask me an IT question and let's figure it out.\n\n"
            "You have 8 messages per day."
        )

        return "OK"

    # --------------------------------
    # /help
    # --------------------------------

    if text == "/help":

        send_message(
            chat_id,
            "I'm Dexter, an IT-focused AI assistant.\n\n"
            "I can help with:\n"
            "• Programming\n"
            "• Web development\n"
            "• Databases\n"
            "• Networking\n"
            "• Cybersecurity\n"
            "• AI & Machine Learning\n"
            "• Operating Systems\n"
            "• APIs\n"
            "• Git & GitHub\n"
            "• Data Structures\n"
            "• Screenshots & IT errors\n\n"
            "You can send up to 8 messages per day."
        )

        return "OK"

    # --------------------------------
    # Detect image
    # --------------------------------

    photo = message.get("photo")

    if photo:

        # Telegram sends multiple sizes.
        # The last one is normally the largest.
        largest_photo = photo[-1]

        file_id = largest_photo["file_id"]

        # Caption = user's question
        caption = message.get("caption", "").strip()

        # Daily limit
        if not can_use(chat_id):

            send_message(
                chat_id,
                "You've reached your 8-message limit for today. "
                "Your limit will reset tomorrow."
            )

            return "OK"

        try:

            image_bytes = download_telegram_file(file_id)

            answer = ask_dexter_with_image(
                image_bytes,
                caption
            )

            send_message(
                chat_id,
                answer
            )

        except Exception as error:

            print("Image processing error:", error)

            send_message(
                chat_id,
                "Sorry, I couldn't analyze that image right now. "
                "Please try again later."
            )

        return "OK"

    # --------------------------------
    # Ignore messages without text
    # --------------------------------

    if not text:
        return "OK"

    # --------------------------------
    # Daily limit
    # --------------------------------

    if not can_use(chat_id):

        send_message(
            chat_id,
            "You've reached your 8-message limit for today. "
            "Your limit will reset tomorrow."
        )

        return "OK"

    # --------------------------------
    # Normal text question
    # --------------------------------

    try:

        answer = ask_dexter(text)

        send_message(
            chat_id,
            answer
        )

    except Exception as error:

        print("Error:", error)

        send_message(
            chat_id,
            "Sorry, I couldn't process your question right now. "
            "Please try again later."
        )

    return "OK"


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )