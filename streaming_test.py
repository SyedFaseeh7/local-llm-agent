import os
from openai import OpenAI
from dotenv import load_dotenv # To load variables in .env file

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")

)

stream = client.chat.completions.create(
        model=os.environ["MODEL"],
        messages=[
            {
                "role":"user",
                "content":"Hi, What is data streaming in 15 words?"
            }
        ],
        stream=True
    )
full_response = "" # We append the full response into message history
for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
                print(piece,end="",flush=True)
                full_response += piece