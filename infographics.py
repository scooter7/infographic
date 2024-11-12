import streamlit as st
import pandas as pd
import openai
import streamlit.components.v1 as components
import plotly.express as px
import io
import base64
from PIL import Image

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# Set up the app title and instructions
st.title("AI-Powered Infographic Creator")
st.write("Upload a CSV or Excel file, describe the visualization you want, and arrange elements on a canvas to create an infographic.")

# Step 1: Upload and Display CSV/Excel Data
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith("csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
    st.write("### Uploaded Data")
    st.write(data)

# Step 2: Process Natural Language for Visualization
st.write("### Describe Your Visualization")
user_input = st.text_input("Describe the type of visualization you want to create:")
chart_img_url = None  # Initialize chart image URL for Fabric.js

if user_input and uploaded_file:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Generate a visualization idea based on this description: {user_input}"}],
        max_tokens=100
    )
    chart_suggestion = response.choices[0].message.content.strip()
    st.write("**Suggested Chart**:", chart_suggestion)

    # Example: Generate a basic Plotly visualization based on suggestion
    try:
        if "bar" in chart_suggestion.lower():
            fig = px.bar(data, x=data.columns[0], y=data.columns[1])
        elif "line" in chart_suggestion.lower():
            fig = px.line(data, x=data.columns[0], y=data.columns[1])
        elif "scatter" in chart_suggestion.lower():
            fig = px.scatter(data, x=data.columns[0], y=data.columns[1])
        else:
            fig = px.histogram(data, x=data.columns[0])

        # Save the Plotly chart as a PNG image
        img_buffer = io.BytesIO()
        fig.write_image(img_buffer, format="png")
        img_buffer.seek(0)
        
        # Convert image to base64 string
        img_base64 = base64.b64encode(img_buffer.read()).decode("utf-8")
        chart_img_url = f"data:image/png;base64,{img_base64}"

        # Display the chart in Streamlit for reference
        st.image(Image.open(io.BytesIO(base64.b64decode(img_base64))), caption="Generated Chart")

    except Exception as e:
        st.write("Error creating chart:", e)

# Step 3: Display and Customize Visualizations on a Movable Canvas
st.write("### Customize Your Infographic")

# Define Fabric.js canvas setup with JavaScript for interactive elements
canvas_html = f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/4.5.0/fabric.min.js"></script>
<canvas id="canvas" width="800" height="600" style="border:1px solid #000000;"></canvas>
<script>
var canvas = new fabric.Canvas('canvas');

// Function to add Plotly chart image to the canvas if available
if ("{chart_img_url}") {{
    fabric.Image.fromURL("{chart_img_url}", function(img) {{
        img.set({{
            left: 100,
            top: 100,
            selectable: true
        }});
        canvas.add(img);
    }});
}}

// Add text to the canvas
function addText() {{
    var text = new fabric.Textbox('Add your text here', {{
        left: 50,
        top: 50,
        fontSize: 20,
        fill: '#333'
    }});
    canvas.add(text);
}}

// Add buttons to add text and save canvas
document.getElementById("addTextButton").onclick = addText;

function saveCanvasAsImage() {{
    var link = document.createElement('a');
    link.href = canvas.toDataURL({{
        format: 'png',
        multiplier: 2
    }});
    link.download = 'infographic.png';
    link.click();
}}
</script>
<button id="addTextButton">Add Text</button>
<button onclick="saveCanvasAsImage()">Download Infographic</button>
"""

# Step 4: Display the interactive canvas
components.html(canvas_html, height=700)
