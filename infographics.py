import streamlit as st
import openai
from PIL import Image, ImageDraw, ImageFont
import io

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# App title and description
st.title("Presentation Creator")
st.write("Upload text and statistics to create stunning presentations on a single slide.")

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

        # Create a single slide using Pillow
        def create_single_slide(content, aspect_ratio):
            # Set dimensions based on aspect ratio
            if aspect_ratio == "16:9":
                width, height = 1280, 720
            elif aspect_ratio == "1:1":
                width, height = 720, 720
            elif aspect_ratio == "9:16":
                width, height = 720, 1280
            else:
                width, height = 1280, 720

            # Create blank canvas
            img = Image.new("RGB", (width, height), color="white")
            draw = ImageDraw.Draw(img)

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

            return img

        # Generate single slide
        slide = create_single_slide(layout_instructions, aspect_ratio)

        # Display the slide
        st.image(slide, caption="Generated Slide", use_column_width=True)

        # Download the slide as an image
        buf = io.BytesIO()
        slide.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("Download Slide", data=buf, file_name="slide.png", mime="image/png")
