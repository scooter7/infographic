import streamlit as st
import pandas as pd
import openai
import json
from PIL import Image
import base64

# Load OpenAI API key from secrets
client = openai.OpenAI(api_key=st.secrets["openai_api_key"])

# Function to generate content using GPT-4o-mini
def generate_content(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0]['message']['content'].strip()

# Function to save the project data as JSON
def save_project_data(canvas_data):
    project_data = {
        "canvas_data": canvas_data
    }
    return json.dumps(project_data)

# Function to load the project data from JSON
def load_project_data(json_data):
    project_data = json.loads(json_data)
    return project_data["canvas_data"]

# Streamlit UI
st.title("Infographic Creator")

# Upload CSV file
csv_file = st.file_uploader("Upload CSV", type=["csv"])
if csv_file:
    df = pd.read_csv(csv_file)
    st.write("Data Preview:")
    st.write(df)

    # Select chart type
    chart_type = st.selectbox("Select Chart Type", ["Line", "Bar", "Area"])
    
    # Generate chart prompt and pass to OpenAI for chart title generation
    chart_prompt = f"Create a {chart_type} chart title for data:\n{df.head().to_string()}"
    chart_title = generate_content(chart_prompt)
    st.write("Suggested Chart Title:", chart_title)
    
    # Display chart (Placeholder - Replace with actual chart generation)
    st.write(f"Chart placeholder: {chart_type} chart with title '{chart_title}'")

# Upload Image file
image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
if image_file:
    img = Image.open(image_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

# Text field customization
st.subheader("Add Text Field")
text_input = st.text_input("Enter text")
font_size = st.slider("Font Size", 10, 100, 30)
font_color = st.color_picker("Font Color", "#000000")
bg_color = st.color_picker("Background Color", "#FFFFFF")
bg_shape = st.selectbox("Background Shape", ["Rectangle", "Pill"])

# JavaScript & HTML for Fabric.js integration
st.subheader("Infographic Canvas")
st.write("Drag elements around the canvas, resize and position them as needed.")

# Initialize canvas
canvas_init = """
<script>
  var canvas = new fabric.Canvas('canvas');
  canvas.setWidth(800);
  canvas.setHeight(600);
</script>
"""

# Load existing project data if provided
if 'loaded_canvas' not in st.session_state:
    st.session_state['loaded_canvas'] = ''

uploaded_project = st.file_uploader("Upload Project", type=["json"])
if uploaded_project:
    project_json = uploaded_project.read().decode("utf-8")
    st.session_state['loaded_canvas'] = load_project_data(project_json)
    st.success("Project loaded successfully!")

# Draw elements from existing project data
canvas_draw_elements = f"""
<script>
  var canvas = new fabric.Canvas('canvas');
  canvas.loadFromJSON({st.session_state['loaded_canvas']});
</script>
"""

# Fabric.js canvas HTML
canvas_html = f"""
<canvas id="canvas"></canvas>
<button onclick="saveCanvas()">Save Project</button>

<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/4.6.0/fabric.min.js"></script>
{canvas_init}
{canvas_draw_elements}

<script>
  function saveCanvas() {{
    var canvas_json = JSON.stringify(canvas);
    var data_uri = 'data:text/json;base64,' + btoa(canvas_json);
    var link = document.createElement('a');
    link.setAttribute('href', data_uri);
    link.setAttribute('download', 'project.json');
    link.click();
  }}

  canvas.add(new fabric.Text('{text_input}', {{
    left: 100,
    top: 100,
    fontSize: {font_size},
    fill: '{font_color}',
    backgroundColor: '{bg_color}',
    padding: 10,
    {('borderRadius: 50%;' if bg_shape == 'Pill' else '')}
  }}));
</script>
"""

# Display the canvas with elements
st.components.v1.html(canvas_html, height=650, scrolling=False)

# Save project button
if st.button("Save Project"):
    st.session_state['canvas_data'] = save_project_data(canvas_draw_elements)
    st.download_button(
        label="Download Project",
        data=st.session_state['canvas_data'],
        file_name="project.json",
        mime="application/json"
    )

# Final download option for the infographic
if st.button("Download Infographic as Image"):
    st.write("Image download functionality to be implemented...")
