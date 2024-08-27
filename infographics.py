import streamlit as st
import pandas as pd
import openai
import json
import plotly.express as px
import plotly.io as pio
import io
from PIL import Image

# Load OpenAI API key from secrets
client = openai.OpenAI(api_key=st.secrets["openai_api_key"])

# Function to generate content using GPT-4o-mini
def interpret_prompt(prompt, df):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Based on the following data: {df.head().to_string()}, {prompt}. Just provide the chart type and the columns to be used."}
        ]
    )
    return response.choices[0].message.content.strip()

# Function to create a chart based on the interpreted instruction and return it as an image
def create_chart_image(columns, df, chart_type):
    if chart_type == "Bar Chart":
        st.write("Generating Bar Chart...")
        if len(columns) == 2:
            # Aggregate data for plotting
            data = df.groupby(columns).size().reset_index(name='counts')
            
            # Plotly Bar Chart
            fig = px.bar(data, x=columns[0], y='counts', color=columns[1], barmode='group',
                         title=f'Bar Chart of {columns[0]} vs {columns[1]}')
        else:
            st.write("Please select exactly two columns for the bar chart.")
            return None
    elif chart_type == "Line Chart":
        st.write("Generating Line Chart...")
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            
            # Plotly Line Chart
            fig = px.line(data, x=columns[0], y='counts', color=columns[1],
                          title=f'Line Chart of {columns[0]} vs {columns[1]}')
        else:
            st.write("Please select exactly two columns for the line chart.")
            return None
    elif chart_type == "Pie Chart":
        st.write("Generating Pie Chart...")
        if len(columns) == 1:
            data = df[columns[0]].value_counts().reset_index()
            data.columns = [columns[0], 'counts']
            
            # Plotly Pie Chart
            fig = px.pie(data, names=columns[0], values='counts',
                         title=f'Pie Chart of {columns[0]}')
        else:
            st.write("Please select exactly one column for the pie chart.")
            return None
    else:
        st.write("Sorry, I couldn't interpret the instruction. Please try another prompt.")
        return None

    # Convert Plotly figure to image
    img_bytes = pio.to_image(fig, format='png')
    img = Image.open(io.BytesIO(img_bytes))
    return img

# Streamlit UI
st.title("Infographic Creator")

# Upload CSV file
csv_file = st.file_uploader("Upload CSV", type=["csv"])
if csv_file:
    df = pd.read_csv(csv_file)
    st.write("Data Preview:")
    st.write(df)

    # Allow the user to select columns via checkboxes
    st.subheader("Select Columns for Chart/Table")
    selected_columns = []
    for column in df.columns:
        if st.checkbox(column):
            selected_columns.append(column)

    # Dropdown to select chart type
    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Pie Chart", "Table"])

    # Generate chart or table based on selected columns and chart type
    if st.button("Generate Chart/Table"):
        if len(selected_columns) > 0:
            chart_img = create_chart_image(selected_columns, df, chart_type)
            if chart_img:
                # Convert the image to base64 for embedding into HTML
                buffered = io.BytesIO()
                chart_img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_html = f'<img id="chart-img" src="data:image/png;base64,{img_str}" />'
                
                # JavaScript to add the image to the fabric.js canvas
                add_image_js = f"""
                <script>
                    var imgElement = document.getElementById('chart-img');
                    var imgInstance = new fabric.Image(imgElement, {{
                        left: 100,
                        top: 100,
                        angle: 0,
                        opacity: 1.0
                    }});
                    canvas.add(imgInstance);
                </script>
                """
                st.markdown(img_html + add_image_js, unsafe_allow_html=True)
        else:
            st.write("Please select at least one column for the chart/table.")

# Text field customization for infographic
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

# Fabric.js canvas HTML
canvas_html = f"""
<canvas id="canvas"></canvas>
<button onclick="saveCanvas()">Save Project</button>

<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/4.6.0/fabric.min.js"></script>
{canvas_init}

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
