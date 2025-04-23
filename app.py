import streamlit as st
import google.generativeai as genai
import dotenv
import os
from PIL import Image
from tavily import TavilyClient

dotenv.load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
tavily_api_key = st.secrets["TAVILY_API_KEY"]
model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

st.set_page_config(page_title="Safety Detector", page_icon="🕵️‍♀️", layout="centered")

SYSTEM_PROMPT = """You are a witty product-safety assistant! I will give you product names. For each one:

1.  Check if the product contains harmful ingredients. If yes, list them.
2.  Give a recommendation score from 1 to 5 (1 = Avoid, 5 = Safe & Awesome).
3.  Provide links to the product from 2 different e-commerce websites (e.g., Walmart, Target). Include the product name in the URL if possible. State the current price next to each link.
4.  Suggest keywords that could be used to find a relevant image for this product online.
5.  Keep your response under 150 words per product. Make it informative but fun with emoticons!"""

def get_product_links(product_name):
    try:
        results = tavily.search(
            query=f"{product_name} site:walmart.com OR site:target.com",
            search_depth="advanced",
            max_results=4,
        )
        links = [result["url"] for result in results["results"] if any(domain in result["url"] for domain in ["walmart.com", "target.com"])]
        
        formatted_links = []
        for url in links:
            if "walmart.com" in url:
                formatted_links.append(f"- 🛒 [View on Walmart]({url})")
            elif "target.com" in url:
                formatted_links.append(f"- 🎯 [View on Target]({url})")
        return "\n".join(formatted_links) if formatted_links else "No direct product links found!"
    except Exception as e:
        return f"Couldn't fetch links: {str(e)}"


def analyze_product(product_name):
    prompt = f"""
    Analyze the safety of the following product: {product_name}
    
    1. Check if it contains harmful ingredients. If yes, list them.
    2. Rate it from 1 (Avoid) to 5 (Safe & Awesome).
    3. Suggest image search keywords.
     Keep your response under 150 words per product. Make it informative but fun with emoticons!!
    """

    try:
        response = model.generate_content(
            [{"role": "user", "parts": SYSTEM_PROMPT}, {"role": "user", "parts": prompt}]
        )
        result_text = response.candidates[0].content.parts[0].text

        # Use Tavily to get real product links
        product_links = get_product_links(product_name)
        result_text += f"\n\n🔗 **Where to Buy:**\n{product_links}"

        return result_text
    except Exception as e:
        return f"Uh oh! Something went wrong: {str(e)}"

        
st.title("Safety Detector 🕵️‍♀️ - Your Witty Product Buddy")
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
