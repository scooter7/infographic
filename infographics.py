import streamlit as st
import openai
from PIL import Image, ImageDraw, ImageFont
import io
import requests

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# Pexels API key for fetching clip art images
pexels_api_key = st.secrets["pexels_api_key"]
headers = {"Authorization": pexels_api_key}

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
st.title("Infographic Generator with Clip Art Images")
st.write("Generate a visually appealing infographic with dynamic content and clip art-style images.")

uploaded_file = st.file_uploader("Upload a text file with your content:", type=["txt"])
manual_input = st.text_area("Or paste your text here:")

# Allow user to select slide background
st.write("Select Slide Background")
background_color = st.color_picker("Pick a background color:", "#ffffff")

# Button to generate infographic
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

            # Define dynamic layout
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
                    img_response = requests.get(images[i])
                    if img_response.status_code == 200:
                        img_overlay = Image.open(io.BytesIO(img_response.content)).resize((80, 80), Image.Resampling.LANCZOS)
                        img.paste(img_overlay, (x + box_width // 2 - 40, y - 90), mask=img_overlay)

            return img

        infographic = create_infographic(structured_content, background_color, clip_art_images)

        # Display the infographic
        st.image(infographic, caption="Generated Infographic", use_column_width=True)

        # Save and allow download
        buf = io.BytesIO()
        infographic.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("Download Infographic", data=buf, file_name="infographic.png", mime="image/png")
