import re
import json
import streamlit as st
from tavily import TavilyClient
from openai_client import call_llm

st.set_page_config(page_title="Trendy Riyadh", layout="wide")
st.title("📍 Trendy Places in Riyadh")
st.markdown("Get casual expert reports on popular **Cafés, Restaurants, and Parks** in Riyadh.")

# Load Tavily client using Streamlit secrets
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# Utility to extract only JSON from LLM output
def extract_json_from_text(text: str):
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    else:
        raise ValueError("No JSON block found in LLM output.")

# Utility to search top 3 entities for a place type
def get_trending_places(place_type: str):
    query = f"trending {place_type} in Riyadh"
    res = tavily.search(query=query, search_depth="advanced")
    top_names = []
    for result in res["results"]:
        title = result.get("title", "")
        match = re.search(r"(?i)([A-Za-zأ-ي0-9\s\-']+)", title)
        if match:
            name = match.group(1).strip()
            if name and name not in top_names:
                top_names.append(name)
        if len(top_names) == 3:
            break
    return top_names

if st.button("🔍 Use Live Web Search + Generate Reports"):
    with st.spinner("Searching the web for trending places in Riyadh..."):

        cafes = get_trending_places("cafes")
        restaurants = get_trending_places("restaurants")
        parks = get_trending_places("parks")

        st.markdown(f"✅ **Top Cafes**: {', '.join(cafes)}")
        st.markdown(f"✅ **Top Restaurants**: {', '.join(restaurants)}")
        st.markdown(f"✅ **Top Parks**: {', '.join(parks)}")

        prompt = f"""
You are a social media trends expert in Riyadh, Saudi Arabia.

Your task:
1. Use the following trending places found by live web search:
   - Cafes: {', '.join(cafes)}
   - Restaurants: {', '.join(restaurants)}
   - Parks: {', '.join(parks)}

2. Write 3 friendly, short reports in **Arabic** (3-5 sentences) combining **one cafe, one restaurant, and one park** per set.
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
