import streamlit as st
import openai
import requests
from PIL import Image, ImageDraw, ImageFont, ImageColor
import io

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# Define the GitHub repository URLs for templates
template_urls = [
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(1).png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(2).png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(3).png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(4).png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography.png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(5).png",
]

# Function to fetch templates
def fetch_templates():
    templates = []
    for url in template_urls:
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            templates.append(img)
        else:
            st.warning(f"Failed to load template from {url}")
    return templates

# App title and description
st.title("Presentation Creator")
st.write("Upload text and statistics to create stunning presentations inspired by template designs.")

# Step 1: User uploads text or enters content
uploaded_file = st.file_uploader("Upload a text file with your content:", type=["txt"])
manual_input = st.text_area("Or paste your text here:")

# Aspect ratio selection
aspect_ratio = st.selectbox("Choose aspect ratio for your presentation slide:", ["16:9", "1:1", "9:16"])

# Generate Presentation button
if st.button("Generate Slide"):
    # Validate input
    if not uploaded_file and not manual_input.strip():
        st.error("Please upload a file or enter text to proceed.")
    else:
        # Read text content
        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
        else:
            content = manual_input

        st.write("Processing your content...")

        # Fetch templates
        templates = fetch_templates()
        if not templates:
            st.error("No templates could be loaded. Please check the repository.")
            st.stop()

        # Choose a template (for now, pick the first one)
        selected_template = templates[0]

        # Generate layout suggestion from GPT-4o-mini
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Design a visually appealing layout based on the user-provided text. Ensure all elements align with the text and data. Do not add or modify user content."},
                {"role": "user", "content": content}
            ]
        )

        # Extract layout instructions
        layout_instructions = response.choices[0].message.content
        st.write("Layout instructions received.")
        st.write("Generating slide...")

        # Create a slide inspired by the template
        def create_slide_with_template(template, content, aspect_ratio):
            # Resize template to match aspect ratio dimensions
            if aspect_ratio == "16:9":
                width, height = 1280, 720
            elif aspect_ratio == "1:1":
                width, height = 720, 720
            elif aspect_ratio == "9:16":
                width, height = 720, 1280
            else:
                width, height = 1280, 720

            template = template.resize((width, height))
            draw = ImageDraw.Draw(template)

            # Set font
            try:
                font = ImageFont.truetype("arial.ttf", size=24)
            except IOError:
                font = ImageFont.load_default()

            # Draw content
            margin = 50
            lines = []
            words = content.split()
            line = []
            for word in words:
                line.append(word)
                text = " ".join(line)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                if text_width > width - margin * 2:
                    lines.append(" ".join(line[:-1]))
                    line = [word]
            lines.append(" ".join(line))

            y = margin
            for line in lines:
                draw.text((margin, y), line, fill="black", font=font)
                bbox = draw.textbbox((0, 0), line, font=font)
                text_height = bbox[3] - bbox[1]
                y += text_height + 10

            return template

        # Generate slide
        slide = create_slide_with_template(selected_template.copy(), content, aspect_ratio)

        # Display the slide
        st.image(slide, caption="Generated Slide", use_column_width=True)

        # Download the slide as an image
        buf = io.BytesIO()
        slide.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("Download Slide", data=buf, file_name="slide.png", mime="image/png")
