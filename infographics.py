import streamlit as st
import pandas as pd
import openai
import json
import matplotlib.pyplot as plt

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

# Function to create a chart based on the interpreted instruction
def create_chart(instruction, df):
    if "bar chart" in instruction.lower() or "column chart" in instruction.lower():
        st.write("Generating Bar Chart...")
        # Extract columns from the instruction
        columns = [col for col in df.columns if col in instruction]
        if len(columns) == 2:
            # Aggregate data for plotting
            data = df.groupby(columns).size().reset_index(name='counts')
            data_pivot = data.pivot(index=columns[0], columns=columns[1], values='counts').fillna(0)
            data_pivot.plot(kind='bar')
            st.pyplot(plt)
        else:
            st.write("Please specify exactly two columns for the bar chart.")
    elif "line chart" in instruction.lower():
        st.write("Generating Line Chart...")
        # Extract columns from the instruction
        columns = [col for col in df.columns if col in instruction]
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            data_pivot = data.pivot(index=columns[0], columns=columns[1], values='counts').fillna(0)
            data_pivot.plot(kind='line')
            st.pyplot(plt)
        else:
            st.write("Please specify exactly two columns for the line chart.")
    elif "table" in instruction.lower():
        st.write("Displaying Data Table...")
        st.write(df)
    else:
        st.write("Sorry, I couldn't interpret the instruction. Please try another prompt.")

# Streamlit UI
st.title("Infographic Creator")

# Upload CSV file
csv_file = st.file_uploader("Upload CSV", type=["csv"])
if csv_file:
    df = pd.read_csv(csv_file)
    st.write("Data Preview:")
    st.write(df)

    # Text field for user to input prompt
    user_prompt = st.text_input("Enter your instruction for creating a chart or table based on the data:")

    if user_prompt:
        # Interpret the prompt using GPT-4o-mini
        instruction = interpret_prompt(user_prompt, df)
        st.write(f"Interpreted Instruction: {instruction}")

        # Generate chart or table based on the interpreted instruction
        create_chart(instruction, df)

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
