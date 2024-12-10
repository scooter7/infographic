import streamlit as st
import openai
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# Define template URL
template_url = "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(1).png"

# Function to fetch the template
def fetch_template(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        st.error("Failed to load the template.")
        return None

# Load the template
template = fetch_template(template_url)

# Bounding boxes for circles (x, y, width, height)
circle_regions = [
    (80, 180, 220, 180),   # Circle 1
    (360, 180, 220, 180),  # Circle 2
    (640, 180, 220, 180),  # Circle 3
    (920, 180, 220, 180),  # Circle 4
    (1200, 180, 220, 180), # Circle 5
]

# Streamlit app setup
st.title("Infographic Generator with Positional Constraints")
st.write("Generate a visually appealing infographic based on your input.")

uploaded_file = st.file_uploader("Upload a text file with your content:", type=["txt"])
manual_input = st.text_area("Or paste your text here:")

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

        # Extract structured content
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Break the following text into structured sections for headings and subheadings."},
                {"role": "user", "content": content},
            ]
        )
        structured_content = response.choices[0].message.content
        st.write("Structured Content:", structured_content)

        # Resize template
        template_resized = template.resize((1400, 800))
        draw = ImageDraw.Draw(template_resized)

        # Set font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        # Function to render text within bounding boxes
        def render_text_in_box(draw, box, text, font):
            x, y, box_width, box_height = box
            words = text.split()
            lines = []
            line = []
            for word in words:
                line.append(word)
                test_line = " ".join(line)
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                if text_width > box_width:
                    lines.append(" ".join(line[:-1]))
                    line = [word]
            lines.append(" ".join(line))

            # Draw each line within the box
            y_offset = y
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_height = bbox[3] - bbox[1]
                if y_offset + text_height > y + box_height:
                    break  # Stop if text exceeds the box height
                draw.text((x, y_offset), line, fill="black", font=font)
                y_offset += text_height + 5

        # Map structured content to circle regions
        sections = structured_content.split("\n\n")  # Split into sections
        for i, box in enumerate(circle_regions):
            if i < len(sections):
                render_text_in_box(draw, box, sections[i], font)

        # Display the infographic
        st.image(template_resized, caption="Generated Infographic", use_column_width=True)

        # Save and allow download
        buf = io.BytesIO()
        template_resized.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("Download Infographic", data=buf, file_name="infographic.png", mime="image/png")
