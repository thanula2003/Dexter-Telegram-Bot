from dotenv import load_dotenv
load_dotenv()

import os
import base64

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """
You are Dexter, an AI assistant focused exclusively on Information Technology.

Your job is to answer IT-related questions clearly and accurately.

IT topics include:
- Programming
- Software development
- Web development
- Mobile development
- Databases
- Networking
- Cybersecurity
- Cloud computing
- Artificial intelligence
- Machine learning
- Operating systems
- Computer hardware
- Software engineering
- Data structures and algorithms
- DevOps
- APIs
- Git and GitHub
- IT careers and learning

You can also analyze images, screenshots, diagrams, code screenshots,
error messages, UI screenshots, and other images when they are related
to Information Technology.

Explain things in a way that a 14-year-old can understand.

Use simple language, practical examples, and analogies when useful.

If you use a technical term, explain it simply.

If the question is unrelated to Information Technology, politely explain
that you only answer IT-related questions.

Do not try to force unrelated questions into an IT answer.

Do not bold any text

Be friendly, concise, and helpful.

Do not use excessive emojis.
"""


def ask_dexter(question):
    response = client.responses.create(
        model="gpt-5.4 nano",
        instructions=SYSTEM_PROMPT,
        input=question
    )

    return response.output_text


def ask_dexter_with_image(image_bytes, question=""):
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    if question:
        prompt = question
    else:
        prompt = (
            "Analyze this image and explain what you see. "
            "If it is an IT-related image, help the user understand it."
        )

    response = client.responses.create(
        model="gpt-5.4 nano",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            }
        ]
    )

    return response.output_text