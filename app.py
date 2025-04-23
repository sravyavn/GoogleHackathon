import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
from tavily import TavilyClient  # Import the Tavily client

# Access your Tavily API key from Streamlit secrets
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

st.set_page_config(page_title="Safety Detective", page_icon="🕵️‍♀️", layout="centered")


def analyze_product(product_name):
    prompt_for_gemini = f"""Analyze the safety of the following product: {product_name}
                    Provide information on harmful ingredients and a safety score (1-5). Also, suggest image keywords."""
    product_links = []
    try:
        # Search for the product on potential e-commerce sites using Tavily
        search_results_walmart = tavily_client.search(query=f"{product_name} on Walmart", search_depth="shallow")
        search_results_target = tavily_client.search(query=f"{product_name} on Target", search_depth="shallow")

        # Extract the first relevant URL if found
        if search_results_walmart.results:
            product_links.append(f"[Walmart Link]({search_results_walmart.results[0].url}) - Price: [Fetch Price]") # You'd need another way to fetch the price
        else:
            product_links.append("Walmart: Product not easily found.")

        if search_results_target.results:
            product_links.append(f"[Target Link]({search_results_target.results[0].url}) - Price: [Fetch Price]") # You'd need another way to fetch the price
        else:
            product_links.append("Target: Product not easily found.")

        gemini_response = model.generate_content(
            [{"role": "user", "parts": SYSTEM_PROMPT}, {"role": "user", "parts": prompt_for_gemini}]
        )
        safety_analysis = gemini_response.candidates[0].content.parts[0].text

        # Append the links to the Gemini's analysis
        full_response = f"{safety_analysis}\n\n**Where to Buy:**\n" + "\n".join(product_links)
        return full_response

    except Exception as e:
        return f"Uh oh! Something went wrong while analyzing and searching: {str(e)}"

st.title("Safety Detective 🕵️‍♀️ - Your Witty Product Buddy")
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
        st.markdown(f"**Safety Detective:** {message['parts']}", unsafe_allow_html=True)
    elif message["role"] == "user":
        st.write(f"**You:** {message['parts']}")
