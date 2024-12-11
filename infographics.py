import streamlit as st
import openai
import requests
import re
from PIL import Image, ImageDraw, ImageFont
import io

# Google Custom Search API setup
google_api_key = st.secrets["google_api_key"]
google_cx = st.secrets["google_cx"]

# Set OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

def extract_concepts_by_section(text):
    """
    Use OpenAI to extract concise, meaningful keywords or phrases from the text.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract a maximum of 3 concise keywords per section from the text. "
                        "Focus on high-level concepts like topics, ideas, or themes. "
                        "Avoid including numeric values, percentages, or excessive details."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        extracted_keywords = response.choices[0].message.content.strip()
        return re.split(r",|\n", extracted_keywords)  # Split by commas or newlines
    except Exception as e:
        st.error(f"Error extracting concepts: {e}")
        return []

def clean_keywords(keywords):
    """
    Clean extracted keywords to remove numbers and unnecessary formatting.
    """
    clean_keywords = []
    for keyword in keywords:
        clean_keyword = re.sub(r"^\d+\.\s*", "", keyword).strip()  # Remove numbering
        if clean_keyword:
            clean_keywords.append(clean_keyword)
    return clean_keywords

def query_google_images(keyword):
    """
    Query Google Custom Search API for a single keyword.
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": google_api_key,
        "cx": google_cx,
        "q": f"{keyword} clip art",  # Keep 'clip art' as part of the query
        "searchType": "image",
        "num": 1,  # Limit results to 1 image for testing
    }
    try:
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            data = response.json()
            st.write("Raw API Response:", data)  # Log the full API response for debugging
            if "items" in data:
                return data["items"][0]["link"]
            else:
                st.warning(f"No results found for '{keyword}' in API response.")
                return None
        else:
            st.error(f"Google API error: {response.status_code} - {response.text}")
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
st.title("Infographic Generator with Proper Keyword Extraction")
st.write("Generate a visually appealing infographic with concise, meaningful keywords and clip-art images.")

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

        # Break content into sections for OpenAI processing
        sections = content.split("\n\n")
        extracted_keywords = []
        for section in sections:
            st.write(f"Processing section: {section}")
            keywords = extract_concepts_by_section(section)
            st.write(f"Raw extracted keywords: {keywords}")
            cleaned_keywords = clean_keywords(keywords)
            st.write(f"Cleaned keywords: {cleaned_keywords}")
            extracted_keywords.extend(cleaned_keywords)

        st.write("All Extracted and Cleaned Keywords:", extracted_keywords)

        # Fetch Google images for each keyword
        google_images = fetch_images_for_keywords(extracted_keywords)
        st.write("Fetched Clip Art Images:")
        for img_url in google_images:
            st.image(img_url, width=150)

        # Placeholder for infographic generation
        st.write("Infographic generation not yet implemented with images.")
