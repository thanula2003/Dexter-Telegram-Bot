import os
from datetime import date

import psycopg
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing")


DAILY_LIMIT = 800


def get_connection():
    return psycopg.connect(DATABASE_URL)


def setup_database():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_usage (
                    user_id BIGINT PRIMARY KEY,
                    usage_date DATE NOT NULL,
                    message_count INTEGER NOT NULL DEFAULT 0
                )
            """)

        connection.commit()


def can_use(user_id):

    today = date.today()

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT usage_date, message_count
                FROM user_usage
                WHERE user_id = %s
            """, (user_id,))

            result = cursor.fetchone()


            # New user
            if result is None:

                cursor.execute("""
                    INSERT INTO user_usage
                    (user_id, usage_date, message_count)
                    VALUES (%s, %s, 1)
                """, (user_id, today))

                connection.commit()

                return True


            usage_date, message_count = result


            # New day
            if usage_date != today:

                cursor.execute("""
                    UPDATE user_usage
                    SET usage_date = %s,
                        message_count = 1
                    WHERE user_id = %s
                """, (today, user_id))

                connection.commit()

                return True


            # Limit reached
            if message_count >= DAILY_LIMIT:

                return False


            # Increase usage
            cursor.execute("""
                UPDATE user_usage
                SET message_count = message_count + 1
                WHERE user_id = %s
            """, (user_id,))

            connection.commit()

            return True