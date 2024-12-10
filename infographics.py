import streamlit as st
import openai
from PIL import Image, ImageDraw, ImageFont
import io
import requests

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# Pexels API key for fetching animated images
pexels_api_key = st.secrets["pexels_api_key"]
headers = {"Authorization": pexels_api_key}

# Function to fetch animated images based on keywords
def fetch_animated_images(keywords):
    search_url = "https://api.pexels.com/v1/search"
    images = []
    for keyword in keywords:
        response = requests.get(search_url, params={"query": keyword, "per_page": 1}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                images.append(data["photos"][0]["src"]["medium"])
    return images

# Streamlit app setup
st.title("Infographic Generator with Slide Background and Animated Images")
st.write("Generate a visually appealing infographic with dynamic content and images.")

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
        structured_content = response.choices[0].message.content
        st.write("Structured Content:", structured_content)

        # Extract keywords (using OpenAI or another NLP approach)
        response_keywords = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract the top 5 keywords relevant to the text for image search."},
                {"role": "user", "content": content},
            ]
        )
        keywords = response_keywords.choices[0].message.content.split(", ")
        st.write("Extracted Keywords:", keywords)

        # Fetch animated images
        animated_images = fetch_animated_images(keywords)
        st.write("Fetched Animated Images:")
        for img_url in animated_images:
            st.image(img_url, width=150)

        # Create infographic from scratch
        def create_infographic(content, background_color, images):
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

            # Define layout positions for circles and text
            circle_positions = [
                (80, 180), (360, 180), (640, 180), (920, 180), (1200, 180)
            ]
            circle_radius = 90
            text_boxes = [
                (80, 380, 220, 180),   # Text for Circle 1
                (360, 380, 220, 180),  # Text for Circle 2
                (640, 380, 220, 180),  # Text for Circle 3
                (920, 380, 220, 180),  # Text for Circle 4
                (1200, 380, 220, 180), # Text for Circle 5
            ]

            # Draw circles and add text
            sections = content.split("\n\n")
            for i, pos in enumerate(circle_positions):
                if i < len(sections):
                    # Draw circle
                    x, y = pos
                    draw.ellipse([x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius], outline="black", width=3)

                    # Add text to corresponding box
                    box_x, box_y, box_width, box_height = text_boxes[i]
                    words = sections[i].split()
                    lines = []
                    line = []
                    for word in words:
                        line.append(word)
                        test_line = " ".join(line)
                        bbox = draw.textbbox((0, 0), test_line, font=font_body)
                        text_width = bbox[2] - bbox[0]
                        if text_width > box_width:
                            lines.append(" ".join(line[:-1]))
                            line = [word]
                    lines.append(" ".join(line))

                    # Draw each line within the text box
                    y_offset = box_y
                    for line in lines:
                        bbox = draw.textbbox((0, 0), line, font=font_body)
                        text_height = bbox[3] - bbox[1]
                        if y_offset + text_height > box_y + box_height:
                            break  # Stop if text exceeds box height
                        draw.text((box_x, y_offset), line, fill="black", font=font_body)
                        y_offset += text_height + 5

            # Add animated images
            for i, img_url in enumerate(images):
                if i < len(circle_positions):
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        # Open the fetched image
                        img_overlay = Image.open(io.BytesIO(img_response.content)).convert("RGBA")
            
                        # Create an alpha mask for the overlay image
                        overlay_width, overlay_height = img_overlay.size
                        alpha_mask = img_overlay.getchannel("A")
            
                        # Resize overlay image if necessary
                        img_overlay = img_overlay.resize((100, 100), Image.ANTIALIAS)
                        alpha_mask = alpha_mask.resize((100, 100), Image.ANTIALIAS)
            
                        # Position the overlay image
                        x, y = circle_positions[i]
            
                        # Paste the image using the alpha mask
                        img.paste(img_overlay, (x - 50, y - 50), alpha_mask)

            return img

        infographic = create_infographic(structured_content, background_color, animated_images)

        # Display the infographic
        st.image(infographic, caption="Generated Infographic", use_column_width=True)

        # Save and allow download
        buf = io.BytesIO()
        infographic.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("Download Infographic", data=buf, file_name="infographic.png", mime="image/png")
