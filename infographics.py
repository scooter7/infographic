import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from io import BytesIO
import base64

# Function to create a chart based on user input
def create_chart(columns, df, chart_type):
    if chart_type == "Bar Chart":
        data = df.groupby(columns).size().reset_index(name='counts')
        fig = px.bar(data, x=columns[0], y='counts', color=columns[1] if len(columns) > 1 else None)
    elif chart_type == "Line Chart":
        data = df.groupby(columns).size().reset_index(name='counts')
        fig = px.line(data, x=columns[0], y='counts', color=columns[1] if len(columns) > 1 else None)
    elif chart_type == "Pie Chart":
        data = df[columns[0]].value_counts().reset_index()
        data.columns = [columns[0], 'counts']
        fig = px.pie(data, names=columns[0], values='counts')
    else:
        fig = None
    return fig

# Function to convert Plotly figure to a base64 string
def fig_to_base64(fig):
    try:
        img_bytes = pio.to_image(fig, format="png")
        return base64.b64encode(img_bytes).decode()
    except Exception as e:
        st.error(f"Error converting figure to image: {e}")
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
    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Pie Chart"])

    # Generate and display the chart
    if st.button("Generate Chart"):
        if len(selected_columns) > 0:
            fig = create_chart(selected_columns, df, chart_type)
            if fig:
                st.plotly_chart(fig)

                # Convert the chart to a base64 string
                img_base64 = fig_to_base64(fig)

                if img_base64:
                    # Display the static image directly in the UI
                    st.image(f"data:image/png;base64,{img_base64}", caption="Chart as Image", use_column_width=True)

                    # Prepare the canvas with the chart image
                    canvas_html = f"""
                    <canvas id="canvas" width="800" height="600"></canvas>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/4.6.0/fabric.min.js"></script>
                    <script>
                        var canvas = new fabric.Canvas('canvas', {{
                            backgroundColor: '#ffffff'
                        }});
                        fabric.Image.fromURL('data:image/png;base64,{img_base64}', function(oImg) {{
                            oImg.scale(0.5);
                            canvas.add(oImg);
                        }});
                    </script>
                    """

                    st.components.v1.html(canvas_html, height=650)
        else:
            st.write("Please select at least one column for the chart.")
