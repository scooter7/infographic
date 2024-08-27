import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import io
from PIL import Image
import base64

# Function to create a chart and return it as an image
def create_chart_image(columns, df, chart_type):
    if chart_type == "Bar Chart":
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.bar(data, x=columns[0], y='counts', color=columns[1], barmode='group', title=f'Bar Chart of {columns[0]} vs {columns[1]}')
        else:
            st.warning("Please select exactly two columns for the bar chart.")
            return None
    elif chart_type == "Line Chart":
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.line(data, x=columns[0], y='counts', color=columns[1], title=f'Line Chart of {columns[0]} vs {columns[1]}')
        else:
            st.warning("Please select exactly two columns for the line chart.")
            return None
    elif chart_type == "Pie Chart":
        if len(columns) == 1:
            data = df[columns[0]].value_counts().reset_index()
            data.columns = [columns[0], 'counts']
            fig = px.pie(data, names=columns[0], values='counts', title=f'Pie Chart of {columns[0]}')
        else:
            st.warning("Please select exactly one column for the pie chart.")
            return None
    else:
        st.error("Invalid chart type.")
        return None

    # Convert Plotly figure to image using Kaleido
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
                
                # JavaScript to add the image to the fabric.js canvas
                canvas_js = f"""
                <script>
                    var canvas = new fabric.Canvas('canvas');
                    canvas.setWidth(800);
                    canvas.setHeight(600);

                    var imgElement = document.createElement('img');
                    imgElement.src = 'data:image/png;base64,{img_str}';
                    imgElement.onload = function () {{
                        var imgInstance = new fabric.Image(imgElement, {{
                            left: 100,
                            top: 100,
                            angle: 0,
                            opacity: 1.0
                        }});
                        canvas.add(imgInstance);
                        canvas.renderAll();
                    }};
                </script>
                """

                # Display the canvas
                st.markdown(f'<canvas id="canvas"></canvas>{canvas_js}', unsafe_allow_html=True)
        else:
            st.warning("Please select at least one column for the chart/table.")

# Save project button
if st.button("Save Project"):
    st.download_button(
        label="Download Project",
        data=st.session_state.get('canvas_data', ''),
        file_name="project.json",
        mime="application/json"
    )

# Final download option for the infographic
if st.button("Download Infographic as Image"):
    st.write("Image download functionality to be implemented...")
