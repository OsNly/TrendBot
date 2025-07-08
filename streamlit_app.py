import re
import json
import os
import requests
import streamlit as st
from openai_client import call_llm

st.set_page_config(page_title="Trendy Riyadh", layout="wide")
st.title("📍 Trendy Places in Riyadh")
st.markdown("Get casual expert reports on popular **Cafés, Restaurants, and Parks** in Riyadh.")

# 🔐 Load Tavily API key from secrets
TAVILY_API_KEY = st.secrets["tavily"]["api_key"]

# --- Helper: Extract JSON array from LLM response ---
def extract_json_from_text(text: str):
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    else:
        raise ValueError("No JSON block found in LLM output.")

# --- Helper: Search Tavily and extract top 3 unique names ---
def get_trending_places(place_type: str):
    query = f"trending {place_type} in Riyadh"
    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    params = {
        "query": query,
        "search_depth": "basic",
        "include_answer": True
    }

    response = requests.post(url, headers=headers, json=params)

    if response.status_code != 200:
        raise Exception(f"Tavily API error: {response.status_code} - {response.text}")

    data = response.json()
    answer_text = data.get("answer", "")

    # Extract candidate names
    found_names = re.findall(r"([A-Za-zأ-ي0-9\s\-\']{3,})", answer_text)
    seen = set()
    unique = []
    for name in found_names:
        clean = name.strip()
        if clean and clean not in seen:
            seen.add(clean)
            unique.append(clean)
        if len(unique) == 3:
            break

    return unique


# --- UI Trigger ---
if st.button("🔍 Use Live Web Search + Generate Reports"):
    with st.spinner("Searching the web for trending places in Riyadh..."):

        try:
            cafes = get_trending_places("cafes")
            restaurants = get_trending_places("restaurants")
            parks = get_trending_places("parks")
        except Exception as e:
            st.error(f"❌ Tavily error: {e}")
            st.stop()

        st.markdown(f"✅ **Top Cafes:** {', '.join(cafes)}")
        st.markdown(f"✅ **Top Restaurants:** {', '.join(restaurants)}")
        st.markdown(f"✅ **Top Parks:** {', '.join(parks)}")

        # 🧠 Prompt for OpenRouter LLM
        prompt = f"""
You are a social media trends expert in Riyadh, Saudi Arabia.

Your task:
1. Use the following trending places found by live web search:
   - Cafes: {', '.join(cafes)}
   - Restaurants: {', '.join(restaurants)}
   - Parks: {', '.join(parks)}

2. Write 3 friendly, short reports in **Arabic** (20-30 sentences) combining **one cafe, one restaurant, and one park** per set.
3. Only return JSON in this exact format:

[
  {{
    "cafe": "اسم الكافيه",
    "restaurant": "اسم المطعم",
    "park": "اسم الحديقة",
    "report": "تقرير باللغة العربية عن الثلاث أماكن"
  }},
  ...
]

Return exactly 3 items.
DO NOT include any text before or after the JSON block.
"""

        with st.expander("🧠 Prompt sent to LLM"):
            st.code(prompt)

        with st.spinner("Generating Arabic trend reports..."):
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
    st.info("Click the button above to search the web and generate trending place reports.")
