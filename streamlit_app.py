import re
import json
import streamlit as st
from openai_client import call_llm

st.set_page_config(page_title="Trendy Riyadh", layout="wide")
st.title("📍 Trendy Places in Riyadh")
st.markdown("Get casual expert reports on popular **Cafés, Restaurants, and Parks** in Riyadh.")

prompt = """
You are a social media trends expert in Riyadh, Saudi Arabia.

Your task:
1. Think of 3 popular cafes, 3 restaurants, and 3 parks currently trending in Riyadh.
2. For each set, write a friendly, short report in Arabic NOT in English (3-5 sentences) combining one cafe, one restaurant, and one park.
3. Only return JSON in this exact format:

[
  {
    "cafe": "Grin",
    "restaurant": "Blu Pizzeria",
    "park": "Wadi Namar",
    "report": "Grin is the go-to café for creatives in Riyadh. Grab your espresso then head to Blu Pizzeria nearby for a wood-fired lunch. Finish the day relaxing at Wadi Namar, where walking trails and lakeside views give the perfect wind-down."
  },
  ...
]
Return exactly 3 items.
DO NOT include any text before or after the JSON block.
"""

def extract_json_from_text(text: str):
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    else:
        raise ValueError("No JSON block found in LLM output.")

if st.button("📊 Generate Trend Reports"):
    with st.spinner("Thinking like a Riyadh influencer..."):

        llm_response = call_llm(prompt)

        try:
            results = extract_json_from_text(llm_response)
            st.success("✅ Here's what's trending:")

            for i, item in enumerate(results, 1):
                with st.container():
                    st.subheader(f"Set {i}")
                    st.markdown(f"**☕ Café:** {item['cafe']}")
                    st.markdown(f"**🍽️ Restaurant:** {item['restaurant']}")
                    st.markdown(f"**🌳 Park:** {item['park']}")
                    st.markdown(f"📌 _{item['report']}_")
                    st.markdown("---")

        except Exception as e:
            st.error(f"❌ Couldn't parse LLM response: {e}")
            st.text("Raw LLM Output:")
            st.code(llm_response)
else:
    st.info("Click the button above to generate trending place reports.")
