import streamlit as st
import openai
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import json
from urllib.parse import urljoin

# GitHub repository URL for template examples
TEMPLATE_REPO_URL = "https://api.github.com/repos/scooter7/infographic/contents/Examples"

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# Pexels API key for fetching clip art images
pexels_api_key = st.secrets["pexels_api_key"]
headers = {"Authorization": pexels_api_key}

# Fetch template example files
def fetch_template_examples():
    response = requests.get(TEMPLATE_REPO_URL)
    if response.status_code == 200:
        templates = []
        for file in response.json():
            if file["name"].endswith(".json"):
                template_response = requests.get(file["download_url"])
                if template_response.status_code == 200:
                    templates.append(json.loads(template_response.content))
        return templates
    else:
        st.error("Unable to fetch templates from GitHub.")
        return []

# Analyze templates for layout guidance
def analyze_templates(templates):
    layout_data = []
    for template in templates:
        layout_data.append(template.get("layout", {}))  # Assume templates include 'layout' keys
    return layout_data

# Function to fetch clip art-style images based on keywords
def fetch_clip_art_images(keywords):
    search_url = "https://api.pexels.com/v1/search"
    images = []
    for keyword in keywords:
        query = f"{keyword} clip art"
        response = requests.get(search_url, params={"query": query, "per_page": 1}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                images.append(data["photos"][0]["src"]["medium"])
    return images

# Streamlit app setup
st.title("Infographic Generator with Template-Based Layouts")
st.write("Generate a visually appealing infographic with dynamic content and clip art-style images.")

uploaded_file = st.file_uploader("Upload a text file with your content:", type=["txt"])
manual_input = st.text_area("Or paste your text here:")

# Allow user to select slide background
st.write("Select Slide Background")
background_color = st.color_picker("Pick a background color:", "#ffffff")

# Fetch and analyze templates
templates = fetch_template_examples()
template_layouts = analyze_templates(templates)

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

        # Fetch clip art images for each section
        clip_art_images = fetch_clip_art_images(keywords)
        st.write("Fetched Clip Art Images:")
        for img_url in clip_art_images:
            st.image(img_url, width=150)

        # Create infographic using template layout
        def create_infographic(content_sections, background_color, images, layout):
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
            title = layout.get("title", "Generated Infographic")
            draw.text((50, 30), title, fill="black", font=font_title)

            # Use template layout for content
            num_sections = len(content_sections)
            for i, section in enumerate(content_sections):
                if i < len(layout.get("boxes", [])):
                    box = layout["boxes"][i]
                    x, y, box_width, box_height = box["x"], box["y"], box["width"], box["height"]

                    # Draw text box
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
                        if text_width > box_width - 20:
                            lines.append(" ".join(line[:-1]))
                            line = [word]
                    lines.append(" ".join(line))

                    y_text = y + 10
                    for line in lines:
                        draw.text((x + 10, y_text), line, fill="black", font=font_body)
                        y_text += 30

                    # Add clip art image
                    if i < len(images):
                        img_response = requests.get(images[i])
                        if img_response.status_code == 200:
                            img_overlay = Image.open(io.BytesIO(img_response.content)).resize((80, 80), Image.Resampling.LANCZOS)
                            img.paste(img_overlay, (x + box_width // 2 - 40, y - 90), mask=img_overlay)

            return img

        # Use the first available layout
        selected_layout = template_layouts[0] if template_layouts else {"title": "Generated Infographic", "boxes": []}
        infographic = create_infographic(structured_content, background_color, clip_art_images, selected_layout)

        # Display the infographic
        st.image(infographic, caption="Generated Infographic", use_column_width=True)

        # Save and allow download
        buf = io.BytesIO()
        infographic.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("Download Infographic", data=buf, file_name="infographic.png", mime="image/png")
