import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env")

if not model:
    raise ValueError("GROQ_MODEL is missing from .env")

llm = ChatGroq(
    model=model,
    temperature=0,
    api_key=api_key
)

response = llm.invoke("Reply with: Groq connection successful!")

print(response.content)