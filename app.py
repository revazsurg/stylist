import streamlit as st
from openai import OpenAI
import os

# Setup Streamlit
st.set_page_config(page_title="Wardrobe Whisperer", page_icon="🧥")
st.title("👗 Wardrobe Whisperer")
st.subheader("Your personal AI stylist")
st.markdown("---")

# Setup OpenAI client (using new SDK style)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === Sidebar: User Profile ===
st.sidebar.header("🧍 User Profile")

name = st.sidebar.text_input("Name", "Sofia")
age = st.sidebar.slider("Age", 18, 60, 28)
gender = st.sidebar.selectbox("Gender", ["female", "male", "non-binary"])
height = st.sidebar.slider("Height (cm)", 140, 200, 168)
body_type = st.sidebar.selectbox("Body Type", ["hourglass", "pear", "rectangle", "athletic", "inverted triangle"])
style_preferences = st.sidebar.multiselect(
    "Style Preferences",
    ["casual", "chic", "boho", "streetwear", "minimalist", "Parisian", "edgy", "elegant"],
    default=["chic", "casual", "Parisian"]
)
climate = st.sidebar.selectbox("Climate", ["hot", "mild", "cold"])
location = st.sidebar.text_input("Location", "Barcelona")
budget = st.sidebar.selectbox("Budget", ["low", "mid", "high"])
favorite_brands = st.sidebar.multiselect("Favorite Brands", ["Zara", "Arket", "Mango", "COS", "H&M"], default=["Zara", "Arket", "Mango"])

# === Main: Wardrobe & Context ===
st.header("🧺 Your Wardrobe")
wardrobe = st.text_area("List your wardrobe items (comma separated)", 
                        "white cropped blouse, high-waisted black jeans, oversized beige blazer, white sneakers, black ankle boots, cream knit sweater")
wardrobe_list = [item.strip() for item in wardrobe.split(",") if item.strip()]

st.header("📅 Context")
event = st.text_input("Event", "coffee date")
season = st.selectbox("Season", ["spring", "summer", "fall", "winter"], index=0)
temperature = st.slider("Temperature (°C)", 0, 40, 20)
rain_expected = st.checkbox("Rain Expected?", value=False)
purchase_enabled = st.checkbox("Enable Shopping Suggestions?", value=True)

# === Generate Prompt and Query GPT-4 ===
if st.button("👚 Get My Outfit"):
    # Build prompt
    prompt = f"""
You are an AI fashion stylist. Your job is to help {name} pick an outfit for a {event} in {location}.

They are {age} years old, {height} cm tall, with a {body_type} body type. Their style is {", ".join(style_preferences)}, and the weather is {temperature}°C in {season}.

They have these wardrobe items: {", ".join(wardrobe_list)}.

Suggest a stylish outfit using their wardrobe. If any items are missing, recommend 1–2 purchasable pieces from their favorite brands ({", ".join(favorite_brands)}), within their {budget} budget.
"""

    with st.spinner("Stylist thinking... 👠"):
        try:
            response = client.chat.completions.create(
                model="gpt-4",  # or use "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are a friendly and stylish AI fashion assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=800
            )

            reply = response.choices[0].message.content
            st.subheader("🪄 AI Stylist Suggestion")
            st.markdown(reply)

        except Exception as e:
            st.error(f"❌ Error from OpenAI: {e}")
