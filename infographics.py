import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import base64
from io import BytesIO
from PIL import Image
import os

# Function to create a chart based on the user's input
def create_chart(columns, df, chart_type):
    fig = None
    if chart_type == "Bar Chart":
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.bar(data, x=columns[0], y='counts', color=columns[1], barmode='group')
        else:
            st.write("Please select exactly two columns for the bar chart.")
    elif chart_type == "Line Chart":
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.line(data, x=columns[0], y='counts', color=columns[1])
        else:
            st.write("Please select exactly two columns for the line chart.")
    elif chart_type == "Pie Chart":
        if len(columns) == 1:
            data = df[columns[0]].value_counts().reset_index()
            data.columns = [columns[0], 'counts']
            fig = px.pie(data, names=columns[0], values='counts')
        else:
            st.write("Please select exactly one column for the pie chart.")
    return fig

# Function to save Plotly figure as an image and convert to base64
def save_chart_as_image(fig):
    img_bytes = pio.to_image(fig, format="png")
    image = Image.open(BytesIO(img_bytes))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    return img_base64

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
    fig = None
    if st.button("Generate Chart/Table"):
        if len(selected_columns) > 0:
            fig = create_chart(selected_columns, df, chart_type)
            if fig:
                st.plotly_chart(fig)
        else:
            st.write("Please select at least one column for the chart/table.")

    # Button to save chart as image and place on canvas
    if fig and st.button("Save Chart as Image"):
        img_base64 = save_chart_as_image(fig)

        # Add the image to the canvas with draggable and resizable functionalities
        canvas_html = f"""
        <canvas id="canvas" width="800" height="600"></canvas>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/4.6.0/fabric.min.js"></script>
        <script>
            var canvas = new fabric.Canvas('canvas');
            fabric.Image.fromURL('data:image/png;base64,{img_base64}', function(img) {{
                img.set({{
                    left: 50,
                    top: 50,
                    angle: 0,
                    padding: 10,
                    cornersize: 10,
                    hasControls: true,
                    hasBorders: true
                }});
                canvas.add(img);
            }});
        </script>
        """

        st.components.v1.html(canvas_html, height=650, scrolling=False)
