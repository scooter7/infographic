import streamlit as st
import pandas as pd
import openai
import json
import plotly.express as px
import plotly.io as pio
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
    fig = None
    if chart_type == "Bar Chart":
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.bar(data, x=columns[0], y='counts', color=columns[1], barmode='group',
                         title=f'Bar Chart of {columns[0]} vs {columns[1]}')
        else:
            st.write("Please select exactly two columns for the bar chart.")
    elif chart_type == "Line Chart":
        if len(columns) == 2:
            data = df.groupby(columns).size().reset_index(name='counts')
            fig = px.line(data, x=columns[0], y='counts', color=columns[1],
                          title=f'Line Chart of {columns[0]} vs {columns[1]}')
        else:
            st.write("Please select exactly two columns for the line chart.")
    elif chart_type == "Pie Chart":
        if len(columns) == 1:
            data = df[columns[0]].value_counts().reset_index()
            data.columns = [columns[0], 'counts']
           
