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

        # Correct way to access the content
        layout_instructions = response.choices[0].message.content
        st.write("Layout instructions received.")

        # Generate image based on layout instructions
        dalle_response = openai.Image.create(
            prompt=f"Generate a professional presentation slide: {layout_instructions}",
            n=1,
            size="1024x1024"
        )

        # Validate and fetch image URL
        image_url = dalle_response["data"][0]["url"]
        try:
            response = requests.get(image_url)
            response.raise_for_status()  # Raise error for invalid responses
            image = Image.open(io.BytesIO(response.content))
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch image: {e}")
            st.stop()

        # Display generated image
        st.image(image, caption="Generated Presentation Slide", use_column_width=True)

        # QA Step: Display content for validation
        st.write("### Quality Assurance Step")
        st.write("Please ensure that the generated slide matches your uploaded text and statistics.")
        st.text_area("Uploaded Content:", value=content, height=200)
        st.image(image, caption="Generated Slide for QA")

        # Download option
        output_path = "generated_presentation.png"
        image.save(output_path)
        st.download_button("Download Slide", data=open(output_path, "rb"), file_name="presentation.png")
