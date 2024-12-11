import streamlit as st
import openai
from PIL import Image, ImageDraw, ImageFont
import io
import requests

# Google Custom Search API setup
google_api_key = st.secrets["google_api_key"]
google_cx = st.secrets["google_cx"]  # Custom Search Engine ID

# Set OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

def extract_concepts_from_text(text):
    """
    Use OpenAI to extract meaningful keywords or core concepts from the input text.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract concise keywords or phrases from the following text for image generation."},
                {"role": "user", "content": text},
            ]
        )
        extracted_keywords = response.choices[0].message.content.strip()
        return extracted_keywords.split(", ")  # Split into individual keywords
    except Exception as e:
        st.error(f"Error extracting concepts from text: {e}")
        return []

def query_google_images(keyword):
    """
    Query Google Custom Search API for a single keyword.
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": google_api_key,
        "cx": google_cx,
        "q": f"{keyword} clip art",
        "searchType": "image",
        "fileType": "png",
        "imgType": "clipart",
        "num": 1,
    }
    try:
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                return data["items"][0]["link"]
            else:
                return None
        else:
            st.error(f"Google API error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error querying Google API for '{keyword}': {e}")
        return None

def fetch_images_for_keywords(keywords):
    """
    Fetch images for a list of keywords, handling failures gracefully.
    """
    images = []
    for keyword in keywords:
        st.write(f"Querying for '{keyword}'...")
        image_url = query_google_images(keyword)
        if image_url:
            st.write(f"Found image for '{keyword}': {image_url}")
            images.append(image_url)
        else:
            st.warning(f"No image found for '{keyword}'.")
    return images

# Streamlit app setup
st.title("Infographic Generator with Focused Keyword Extraction")
st.write("Generate a visually appealing infographic with dynamic content and clip art images.")

uploaded_file = st.file_uploader("Upload a text file with your content:", type=["txt"])
manual_input = st.text_area("Or paste your text here:")

# Allow user to select slide background
st.write("Select Slide Background")
background_color = st.color_picker("Pick a background color:", "#ffffff")

if st.button("Generate Infographic"):
    if not uploaded_file and not manual_input.strip():
        st.error("Please provide text input.")
    else:
        # Read content
        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
        else:
            content = manual_input

        st.write("Processing your content...")

        # Extract concise keywords using OpenAI
        extracted_keywords = extract_concepts_from_text(content)
        st.write("Extracted Keywords:", extracted_keywords)

        # Fetch Google images for each keyword
        google_images = fetch_images_for_keywords(extracted_keywords)
        st.write("Fetched Clip Art Images:")
        for img_url in google_images:
            st.image(img_url, width=150)

        # Placeholder for infographic generation
        st.write("Infographic generation not yet implemented with images.")
