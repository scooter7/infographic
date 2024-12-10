import streamlit as st
import openai
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# App title and description
st.title("Presentation Creator")
st.write("Upload text and statistics to create stunning presentations in multiple aspect ratios.")

# Step 1: User uploads text or enters content
uploaded_file = st.file_uploader("Upload a text file with your content:", type=["txt"])
manual_input = st.text_area("Or paste your text here:")

# Aspect ratio selection
aspect_ratio = st.selectbox("Choose aspect ratio for your presentation:", ["16:9", "1:1", "9:16"])

# Generate Presentation button
if st.button("Generate Presentation"):
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

        # Simulate image generation (you need to integrate Stable Diffusion or a similar service here)
        st.write("Image generation is not directly supported via OpenAI. Use an external tool like Stable Diffusion to generate images.")

        # Placeholder for QA and user validation
        st.write("### Quality Assurance Step")
        st.write("Please ensure that the generated instructions match your uploaded text and statistics.")
        st.text_area("Uploaded Content:", value=content, height=200)
        st.write(f"Layout Instructions: {layout_instructions}")

        # Simulate image download option
        st.download_button("Download Layout Instructions", data=layout_instructions, file_name="layout_instructions.txt")
