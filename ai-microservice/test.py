import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("Success! Groq says:", completion.choices[0].message.content)
except Exception as e:
    print("Error Type:", type(e).__name__)
    print("Error Details:", e)