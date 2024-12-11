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

# Fetch clip-art images using Google Image Search
import re
import requests

def preprocess_keywords(text):
    """
    Preprocess and clean the text to extract individual keywords for querying.
    Removes numbering, splits multi-term lines, and ensures clean keywords.
    """
    # Split text into lines
    lines = text.splitlines()
    keywords = []
    for line in lines:
        # Remove numbering (e.g., "1.") and extra spaces
        clean_line = re.sub(r"^\d+\.\s*", "", line).strip()
        if clean_line:
            # Split lines with multiple terms by common delimiters
            split_terms = re.split(r"[,\-\n]+", clean_line)
            for term in split_terms:
                term = term.strip()
                if term:
                    keywords.append(term)
    return keywords

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
    images = {}
    for keyword in keywords:
        st.write(f"Querying for '{keyword}'...")
        image_url = query_google_images(keyword)
        if image_url:
            st.write(f"Found image for '{keyword}': {image_url}")
            images[keyword] = image_url
        else:
            st.warning(f"No image found for '{keyword}'.")
    return images

# Example Input and Testing
if st.button("Test New Approach"):
    raw_text = """
    1. AI Adoption
    2. AI Impact
    3. AI Training
    4. Workplace Solutions
    5. Career Development
    """
    st.write("Raw Input Text:", raw_text)

    # Preprocess keywords
    keywords = preprocess_keywords(raw_text)
    st.write("Preprocessed Keywords:", keywords)

    # Fetch images for keywords
    images = fetch_images_for_keywords(keywords)
    st.write("Fetched Images:")
    for keyword, img_url in images.items():
        st.write(f"Keyword: {keyword}")
        st.image(img_url, width=150)

# Streamlit app setup
st.title("Infographic Generator with Google Image Search")
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

        # Extract structured content and keywords
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Break the following text into structured sections and extract main keywords for image generation."},
                {"role": "user", "content": content},
            ]
        )
        structured_content = response.choices[0].message.content.strip().split("\n\n")
        st.write("Structured Content:", structured_content)

        # Extract keywords
        response_keywords = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract the top 5 keywords relevant to the text for image search."},
                {"role": "user", "content": content},
            ]
        )
        keywords = response_keywords.choices[0].message.content.strip().split(", ")
        st.write("Extracted Keywords:", keywords)

        # Fetch Google images for each section
        google_images = fetch_google_images(keywords)
        st.write("Fetched Clip Art Images:")
        for img_url in google_images:
            st.image(img_url, width=150)

        # Create infographic
        def create_infographic(content_sections, background_color, images):
            # Create a blank canvas with background color
            width, height = 1400, 800
            img = Image.new("RGB", (width, height), background_color)
            draw = ImageDraw.Draw(img)

            # Define fonts
            try:
                font_title = ImageFont.truetype("arial.ttf", 40)
                font_body = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font_title = ImageFont.load_default()
                font_body = ImageFont.load_default()

            # Draw title
            title = "Generated Infographic"
            draw.text((50, 30), title, fill="black", font=font_title)

            # Layout based on the number of sections
            num_sections = len(content_sections)
            box_width = 300
            box_height = 200
            margin = 50
            x_offset = (width - (box_width + margin) * num_sections) // 2

            for i, section in enumerate(content_sections):
                x = x_offset + i * (box_width + margin)
                y = height // 2 - box_height // 2

                # Draw rectangular text box
                draw.rectangle([x, y, x + box_width, y + box_height], outline="black", width=3)

                # Add text to the box
                words = section.split()
                lines = []
                line = []
                for word in words:
                    line.append(word)
                    test_line = " ".join(line)
                    bbox = draw.textbbox((0, 0), test_line, font=font_body)
                    text_width = bbox[2] - bbox[0]
                    if text_width > box_width - 20:  # Allow padding inside the box
                        lines.append(" ".join(line[:-1]))
                        line = [word]
                lines.append(" ".join(line))

                y_text = y + 10
                for line in lines:
                    draw.text((x + 10, y_text), line, fill="black", font=font_body)
                    y_text += 30

                # Add clip art image
                if i < len(images):
                    try:
                        img_response = requests.get(images[i])
                        if img_response.status_code == 200:
                            img_overlay = Image.open(io.BytesIO(img_response.content)).resize((80, 80), Image.Resampling.LANCZOS)
                            img.paste(img_overlay, (x + box_width // 2 - 40, y - 90), mask=img_overlay)
                        else:
                            st.warning(f"Failed to fetch image from {images[i]}")
                    except Exception as e:
                        st.error(f"Error loading image from {images[i]}: {e}")

            return img

        infographic = create_infographic(structured_content, background_color, google_images)

        # Display the infographic
        st.image(infographic, caption="Generated Infographic", use_column_width=True)

        # Save and allow download
        buf = io.BytesIO()
        infographic.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("Download Infographic", data=buf, file_name="infographic.png", mime="image/png")
