# openai_client.py
import streamlit as st
from openai import OpenAI

# Load OpenRouter API Key from Streamlit secrets
OPENROUTER_API_KEY = st.secrets["openrouter"]["api_key"]

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "your-app-name",
        "X-Title": "openrouter-integration"
    }
)

MODEL = "google/gemini-2.0-flash-exp:free"

def call_llm(prompt: str, temperature: float = 0.0) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return resp.choices[0].message.content
