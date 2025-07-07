import streamlit as st
from langchain_core.prompts import PromptTemplate
from openai_client import call_llm 
import json

st.set_page_config(page_title="Trendy Riyadh", layout="wide")

st.title("📍 Trendy Places in Riyadh")
st.markdown("Get casual expert reports on popular **Cafés, Restaurants, and Parks** in Riyadh.")


prompt = """
You are a social media trends expert in Riyadh, Saudi Arabia.
Your goal is:
1- Find 3 sets of trendy [Cafes, Restaurants, Parks] in Riyadh.
2- Write a casual report in Arabic on (one cafe, one restaurant, one park) in Riyadh for each combination of the three sets.
Each report should be 3-5 sentences max, friendly and informative.
Output as JSON with this format:
[
  {"cafe": "...", "restaurant": "...", "park": "...", "report": "..."},
  ...
]
"""


if st.button("📊 Generate Trend Reports"):
    with st.spinner("Thinking like a Riyadh influencer..."):
        prompt = visual_prompt
        llm_response = call_llm(prompt)

        try:
            results = json.loads(llm_response)
            st.success("Done! Here's what’s hot in Riyadh 🔥")

            for i, item in enumerate(results, 1):
                with st.container():
                    st.subheader(f"Set {i}")
                    st.markdown(f"**☕ Café:** {item['cafe']}")
                    st.markdown(f"**🍽️ Restaurant:** {item['restaurant']}")
                    st.markdown(f"**🌳 Park:** {item['park']}")
                    st.markdown(f"📌 _{item['report']}_")
                    st.markdown("---")

        except json.JSONDecodeError:
            st.error("❌ Couldn't parse LLM response. Try again or check the prompt.")
            st.text("Raw LLM Output:")
            st.code(llm_response)

else:
    st.info("Click the button above to generate trending place reports.")   
