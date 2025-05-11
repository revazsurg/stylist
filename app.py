import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

# Setup Streamlit
st.set_page_config(page_title="Wardrobe Whisperer", page_icon="🧥")
st.title("👗 Wardrobe Whisperer")
st.subheader("Your personal AI stylist")
st.markdown("---")

# OpenAI API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🔠 Function: GPT-4o-powered Georgian localization
def localize_to_georgian(text):
    examples = """
EN: “Try this blazer with cropped trousers and sneakers for a laid-back brunch.”
KA: “ამ შტრიხებით თქვენს ბრანჩის სტილს მეტი სინატიფე და სიმარტივე დაემატება — შერჩიეთ ბრეზერი და მოკლე შარვლები კომფორტული კედებით.”

EN: “Throw on a lightweight trench for those unpredictable spring evenings.”
KA: “გაზაფხულის მოულოდნელ სიცივეს დახვეწილად შეხვდით — მსუბუქი ტრენჩი იდეალური არჩევანია.”

EN: “Opt for neutral tones and simple lines to create a minimalist chic look.”
KA: “ნეიტრალური ფერები და სუფთა ხაზები დაგეხმარებათ მინიმალისტურ, გემოვნებიან იმიჯში.”
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a native Georgian fashion stylist translating for Georgian women. Use natural Georgian and elegant stylist language. Here are some examples:\n" + examples},
            {"role": "user", "content": text}
        ],
        temperature=0.7,
        max_tokens=700
    )
    return response.choices[0].message.content.strip()

# 🔍 Vision tagging for clothing images
def gpt4_vision_tag(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    prompt = "Describe this clothing item in a short, ecommerce-style phrase (e.g., 'cream wool blazer' or 'black leather sneakers'). Avoid extra commentary."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

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

# === Wardrobe: Text and Image Upload ===
st.header("🧺 Your Wardrobe")
wardrobe = st.text_area("List your wardrobe items (comma separated)",
                        "white cropped blouse, high-waisted black jeans, oversized beige blazer, white sneakers, black ankle boots, cream knit sweater")
wardrobe_list = [item.strip() for item in wardrobe.split(",") if item.strip()]

st.header("🖼️ Upload Wardrobe Images")
uploaded_images = st.file_uploader("Upload images of your clothing items", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

tagged_items = []
if uploaded_images:
    st.info("Give it a moment... each item will be tagged using GPT-4 Vision.")
    for image_file in uploaded_images:
        image = Image.open(image_file)
        st.image(image, caption="Uploaded", width=150)
        tag = gpt4_vision_tag(image_file.getvalue())
        user_tag = st.text_input(f"Edit tag for this item:", tag, key=image_file.name)
        if st.button(f"Add '{user_tag}' to wardrobe", key=f"add_{image_file.name}"):
            tagged_items.append(user_tag)

wardrobe_list.extend(tagged_items)

# === Context & Toggle ===
st.header("📅 Context")
event = st.text_input("Event", "coffee date")
season = st.selectbox("Season", ["spring", "summer", "fall", "winter"], index=0)
temperature = st.slider("Temperature (°C)", 0, 40, 20)
rain_expected = st.checkbox("Rain Expected?", value=False)
purchase_enabled = st.checkbox("Enable Shopping Suggestions?", value=True)

if "show_in_georgian" not in st.session_state:
    st.session_state["show_in_georgian"] = True

st.session_state["show_in_georgian"] = st.checkbox("🇬🇪 Show output in Georgian", value=st.session_state["show_in_georgian"])


# === Generate Outfit Suggestion ===
if st.button("👚 Get My Outfit"):
    # Prompt
    prompt = f"""
You are an AI fashion stylist. Your job is to help {name} pick an outfit for a {event} in {location}.

They are {age} years old, {height} cm tall, with a {body_type} body type. Their style is {", ".join(style_preferences)}, and the weather is {temperature}°C in {season}.

They have these wardrobe items: {", ".join(wardrobe_list)}.

Suggest a stylish outfit using their wardrobe. If any items are missing, recommend 1–2 purchasable pieces from their favorite brands ({", ".join(favorite_brands)}), within their {budget} budget.
"""

    with st.spinner("Stylist thinking... 👠"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a friendly and stylish AI fashion assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=800
            )
            reply = response.choices[0].message.content.strip()

            if st.session_state["show_in_georgian"]:
                st.subheader("🪄 სტილისტის რჩევა ქართულად")
                ge_reply = localize_to_georgian(reply)
                st.markdown(ge_reply)
            else:
                st.subheader("🪄 AI Stylist Suggestion")
                st.markdown(reply)

        except Exception as e:
            st.error(f"❌ Error from OpenAI: {e}")
