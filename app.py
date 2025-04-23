import streamlit as st
import google.generativeai as genai
import dotenv
import os
from PIL import Image

dotenv.load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

st.set_page_config(page_title="The Wise Buy Buddy", page_icon="🕵️‍♀️", layout="centered")

SYSTEM_PROMPT = """You are a witty product-safety assistant! I will give you a product name OR a chemical name. For each input:

1.  Identify if the product contains harmful ingredients OR if the chemical itself is considered harmful. If yes, list the harmful ingredient(s) or describe the potential hazards of the chemical. Also, briefly categorize the type of harm (e.g., "Potential skin irritant ⚠️," "May be harmful if ingested 💀").
2.  Give a recommendation score from 1 to 5 using both a number and a visual icon: 🔴 (Avoid), 🟡 (Proceed with Caution), 🟢 (Generally Safe), 🔵 (Awesome!). Add a very short "Why the Score?" justification (e.g., "Score: 2 🟡 - Contains known irritants.").
3.  Suggest keywords that could be used to find a relevant image online 🖼️.
4.  Include a very brief "Fun Fact" or "Did You Know?" snippet related to the product or chemical. 🤔💡
5.  If the product has harmful ingredients, briefly suggest a "Safer Alternative" if one readily comes to mind 🌱.
6.  Keep your response informative but fun and under 150 words per input, using emoticons or image suggestions to enhance the tone 😄. You can also include a very short, witty tagline for the product based on the safety assessment (e.g., for a score of 1: "Run. Just run. 🏃💨")."""


def analyze_product(product_name):
    prompt = f"""Analyze the safety of the following product: {product_name}
            Provide information on harmful ingredients, a safety score (1-5), and links to page with that product online (with prices). Also, suggest image keywords."""
    try:
        response = model.generate_content(
            [{"role": "user", "parts": SYSTEM_PROMPT}, {"role": "user", "parts": prompt}]
        )
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        return f"Uh oh! Something went wrong: {str(e)}"
st.title("The Wise Buy Buddy 🕵️‍♀️ - Your Ingredient Safety Checker")
st.markdown(
    "<h4 style='text-align: center; color: gray;'>Drop a product name, and I’ll inspect it like Sherlock—with a safety score and a dash of sass 🔍💁‍♀️</h4>",
    unsafe_allow_html=True
)
# Add background color and image styling using inline CSS
st.markdown("""
    <style>
        .main {
            background-color: #9bf8f5;
            padding: 20px;
        }
        .stApp {
            background-color: #acfa84;
        }
        .banner-img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 60%;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Add banner image
st.image(
    "https://www.sesotec.com/sites/593fc2aac25e5b0640a20ff8/content_entry5996a921c25e5b2c7874b55f/5e2ace13d1468d59c7c8d814/files/food-safety-lebensmittel-lupe.jpg",
    caption="🔍 Ensuring Product Safety, One product at a Time",
    use_container_width=True
)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

user_input = st.chat_input("Enter a product name:")

if user_input:
    st.session_state["messages"].append({"role": "user", "parts": user_input})
    safety_analysis = analyze_product(user_input)
    st.session_state["messages"].append({"role": "model", "parts": safety_analysis})

for message in st.session_state["messages"]:
    if message["role"] == "model":
        st.markdown(f"**Safety Sleuth:** {message['parts']}", unsafe_allow_html=True)
    elif message["role"] == "user":
        st.write(f"**You:** {message['parts']}")
