import streamlit as st
import pandas as pd
import openai
import plotly.express as px
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

# Function to create a chart based on the interpreted instruction
def create_chart(columns, df, chart_type):
    if chart_type == "Bar Chart":
        st.write("Generating Bar Chart...")
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.bar(data, x=columns[0], y='counts', color=columns[1], barmode='group',
                         title=f'Bar Chart of {columns[0]} vs {columns[1]}')
            return fig
        else:
            st.write("Please select exactly two columns for the bar chart.")
            return None
    elif chart_type == "Line Chart":
        st.write("Generating Line Chart...")
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.line(data, x=columns[0], y='counts', color=columns[1],
                          title=f'Line Chart of {columns[0]} vs {columns[1]}')
            return fig
        else:
            st.write("Please select exactly two columns for the line chart.")
            return None
    elif chart_type == "Pie Chart":
        st.write("Generating Pie Chart...")
        if len(columns) == 1:
            data = df[columns[0]].value_counts().reset_index()
            data.columns = [columns[0], 'counts']
            fig = px.pie(data, names=columns[0], values='counts',
                         title=f'Pie Chart of {columns[0]}')
            return fig
        else:
            st.write("Please select exactly one column for the pie chart.")
            return None
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
    if st.button("Generate Chart/Table"):
        if len(selected_columns) > 0:
            fig = create_chart(selected_columns, df, chart_type)
            if fig:
                # Convert Plotly figure to image
                img_bytes = fig.to_image(format="png")
                st.image(img_bytes)  # Display image directly in Streamlit

                # Convert to PIL Image for Fabric.js
                image = Image.open(io.BytesIO(img_bytes))
                image.save('chart_image.png')

                # Display the canvas with the image embedded
                canvas_html = f"""
                <canvas id="canvas"></canvas>
                <button onclick="saveCanvas()">Save Project</button>

                <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/4.6.0/fabric.min.js"></script>

                <script>
                    var canvas = new fabric.Canvas('canvas');
                    fabric.Image.fromURL('chart_image.png', function(img) {{
                        img.set({{
                            left: 100,
                            top: 100,
                            angle: 0,
                            padding: 10,
                            cornersize: 10
                        }});
                        canvas.add(img).renderAll();
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
                st.components.v1.html(canvas_html, height=650, scrolling=False)
        else:
            st.write("Please select at least one column for the chart/table.")
