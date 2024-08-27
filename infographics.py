import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import plotly.io as pio
import io

# Function to create a chart based on the user's input
def create_chart(columns, df, chart_type):
    fig = None
    if chart_type == "Bar Chart":
        st.write("Generating Bar Chart...")
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.bar(data, x=columns[0], y='counts', color=columns[1], barmode='group',
                         title=f'Bar Chart of {columns[0]} vs {columns[1]}')
        else:
            st.write("Please select exactly two columns for the bar chart.")
    elif chart_type == "Line Chart":
        st.write("Generating Line Chart...")
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.line(data, x=columns[0], y='counts', color=columns[1],
                          title=f'Line Chart of {columns[0]} vs {columns[1]}')
        else:
            st.write("Please select exactly two columns for the line chart.")
    elif chart_type == "Pie Chart":
        st.write("Generating Pie Chart...")
        if len(columns) == 1:
            data = df[columns[0]].value_counts().reset_index()
            data.columns = [columns[0], 'counts']
            fig = px.pie(data, names=columns[0], values='counts',
                         title=f'Pie Chart of {columns[0]}')
        else:
            st.write("Please select exactly one column for the pie chart.")
    return fig

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
        # Save the chart as an image
        img_bytes = io.BytesIO()
        pio.write_image(fig, img_bytes, format='png')
        img_bytes.seek(0)
        image = Image.open(img_bytes)
        
        # Display the image on a canvas with drag-and-drop functionality
        st.write("Drag the image around to position it.")
        
        canvas_html = f"""
        <canvas id="canvas" width="800" height="600"></canvas>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/4.6.0/fabric.min.js"></script>
        <script>
            var canvas = new fabric.Canvas('canvas');
            fabric.Image.fromURL('data:image/png;base64,{image_to_base64(image)}', function(img) {{
                img.set({{
                    left: 100,
                    top: 100,
                    angle: 0,
                    padding: 10,
                    cornersize: 10
                }});
                canvas.add(img);
            }});
        </script>
        """

        st.components.v1.html(canvas_html, height=650, scrolling=False)

def image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return buffered.getvalue().decode("latin1")

