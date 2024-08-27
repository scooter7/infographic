import streamlit as st
import pandas as pd
import openai
import plotly.express as px
import base64
from io import BytesIO

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
def create_chart(columns, df, chart_type):
    if chart_type == "Bar Chart":
        st.write("Generating Bar Chart...")
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.bar(data, x=columns[0], y='counts', color=columns[1], barmode='group',
                         title=f'Bar Chart of {columns[0]} vs {columns[1]}')
            buf = BytesIO()
            fig.write_image(buf, format="png")
            buf.seek(0)
            return base64.b64encode(buf.read()).decode("utf-8")
        else:
            st.write("Please select exactly two columns for the bar chart.")
    elif chart_type == "Line Chart":
        st.write("Generating Line Chart...")
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.line(data, x=columns[0], y='counts', color=columns[1],
                          title=f'Line Chart of {columns[0]} vs {columns[1]}')
            buf = BytesIO()
            fig.write_image(buf, format="png")
            buf.seek(0)
            return base64.b64encode(buf.read()).decode("utf-8")
        else:
            st.write("Please select exactly two columns for the line chart.")
    elif chart_type == "Pie Chart":
        st.write("Generating Pie Chart...")
        if len(columns) == 1:
            data = df[columns[0]].value_counts().reset_index()
            data.columns = [columns[0], 'counts']
            fig = px.pie(data, names=columns[0], values='counts',
                         title=f'Pie Chart of {columns[0]}')
            buf = BytesIO()
            fig.write_image(buf, format="png")
            buf.seek(0)
            return base64.b64encode(buf.read()).decode("utf-8")
        else:
            st.write("Please select exactly one column for the pie chart.")
    elif chart_type == "Table":
        st.write("Displaying Data Table...")
        st.write(df)
        return None
    else:
        st.write("Sorry, I couldn't interpret the instruction. Please try another prompt.")
        return None

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
    chart_base64 = None
    if st.button("Generate Chart/Table"):
        if len(selected_columns) > 0:
            chart_base64 = create_chart(selected_columns, df, chart_type)
            if chart_base64:
                st.write("Chart created successfully.")
            else:
                st.write("No chart image to display.")
        else:
            st.write("Please select at least one column for the chart/table.")

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
    """

    if chart_base64:
        canvas_html += f"""
        <script>
          fabric.Image.fromURL('data:image/png;base64,{chart_base64}', function(img) {{
              img.set({{
                  left: 50,
                  top: 50,
                  angle: 0,
                  padding: 10,
                  cornersize: 10
              }});
              canvas.add(img);
          }});
          
          function saveCanvas() {{
            var canvas_json = JSON.stringify(canvas);
            var data_uri = 'data:text/json;base64,' + btoa(canvas_json);
            var link = document.createElement('a');
            link.setAttribute('href', data_uri);
            link.setAttribute('download', 'project.json');
            link.click();
          }}
        </script>
        """

    # Text field customization for infographic
    st.subheader("Add Text Field")
    text_input = st.text_input("Enter text")
    font_size = st.slider("Font Size", 10, 100, 30)
    font_color = st.color_picker("Font Color", "#000000")
    bg_color = st.color_picker("Background Color", "#FFFFFF")
    bg_shape = st.selectbox("Background Shape", ["Rectangle", "Pill"])

    # Add text customization to canvas
    canvas_html += f"""
    <script>
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
