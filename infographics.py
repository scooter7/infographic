import streamlit as st
import openai
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# Define template URLs
template_urls = [
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(1).png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(2).png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(3).png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(4).png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography.png",
    "https://github.com/scooter7/infographic/raw/main/Examples/infography%20(5).png",
]

# Function to fetch templates
def fetch_templates(urls):
    templates = []
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            templates.append(img)
        else:
            st.warning(f"Failed to load template from {url}")
    return templates

# Load templates
templates = fetch_templates(template_urls)

# App title and description
st.title("Infographic Generator")
st.write("Generate a visually appealing infographic based on your input.")

# Step 1: User uploads text or enters content
uploaded_file = st.file_uploader("Upload a text file with your content:", type=["txt"])
manual_input = st.text_area("Or paste your text here:")

# Step 2: Template Selection
if templates:
    template_names = [f"Template {i+1}" for i in range(len(templates))]
    selected_template_idx = st.selectbox("Select a template for your infographic:", range(len(templates)), format_func=lambda x: template_names[x])
    selected_template = templates[selected_template_idx]
else:
    st.error("No templates could be loaded. Please check the repository.")
    st.stop()

# Step 3: Aspect ratio selection
aspect_ratio = st.selectbox("Choose aspect ratio for your presentation slide:", ["16:9", "1:1", "9:16"])

# Generate Presentation button
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
                {"role": "system", "content": "Break the following text into structured sections with headings, subheadings, and bullet points. Preserve the original meaning and ensure logical structure."},
                {"role": "user", "content": content},
            ]
        )
        structured_content = response.choices[0].message.content
        st.write("Structured Content:", structured_content)

        # Resize template based on aspect ratio
        if aspect_ratio == "16:9":
            width, height = 1280, 720
        elif aspect_ratio == "1:1":
            width, height = 720, 720
        elif aspect_ratio == "9:16":
            width, height = 720, 1280
        else:
            width, height = 1280, 720

        template_resized = selected_template.resize((width, height))

        # Create infographic using the selected template
        def create_infographic(template, content):
            img = template.copy()
            draw = ImageDraw.Draw(img)

            # Set font
            try:
                font_title = ImageFont.truetype("arial.ttf", 40)
                font_body = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font_title = ImageFont.load_default()
                font_body = ImageFont.load_default()

            # Define content placement regions (coordinates)
            title_region = (50, 30)  # (x, y)
            text_region_start = (50, 120)  # (x, y)

            # Draw title (if exists in content)
            title = "Generated Infographic"  # Replace or refine based on structured_content if needed
            draw.text(title_region, title, fill="black", font=font_title)

            # Draw structured content as body text
            y_offset = text_region_start[1]
            for line in content.split("\n"):
                draw.text((text_region_start[0], y_offset), line.strip(), fill="black", font=font_body)
                _, text_height = font_body.getsize(line)
                y_offset += text_height + 10  # Add line spacing

            return img

        # Generate infographic
        infographic = create_infographic(template_resized, structured_content)

        # Display the infographic
        st.image(infographic, caption="Generated Infographic", use_column_width=True)

        # Save and allow download
        buf = io.BytesIO()
        infographic.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("Download Infographic", data=buf, file_name="infographic.png", mime="image/png")
