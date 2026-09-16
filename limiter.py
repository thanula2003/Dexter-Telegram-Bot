import json
import os
from datetime import date


FILE = "data/users.json"
DAILY_LIMIT = 80


def load_users():
    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as file:
        return json.load(file)


def save_users(users):
    os.makedirs("data", exist_ok=True)

    with open(FILE, "w") as file:
        json.dump(users, file, indent=4)


def can_use(user_id):
    users = load_users()

    user_id = str(user_id)
    today = str(date.today())

    if user_id not in users:
        users[user_id] = {
            "date": today,
            "count": 0
        }

    if users[user_id]["date"] != today:
        users[user_id] = {
            "date": today,
            "count": 0
        }

    if users[user_id]["count"] >= DAILY_LIMIT:
        save_users(users)
        return False

    users[user_id]["count"] += 1

    save_users(users)

    return True