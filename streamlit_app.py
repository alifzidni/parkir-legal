import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_autorefresh import st_autorefresh
from PIL import Image
import requests
from io import BytesIO

# Set up the Streamlit page configuration
st.set_page_config(page_title="Illegal Parking Monitoring", page_icon="🚬", layout="wide")

# Title and description
st.title("Illegal Parking Monitoring")
st.subheader("📘 Capstone Project Group 26")
st.write(
    """
    A real-time dashboard connecting to a Google Spreadsheet to monitor illegal parking activity. 
    View live detections, analyze trends, and explore historical data.
    """
)

# Real-time clock
st.subheader("⏰ Current Time (UTC+7)")
clock_placeholder = st.empty()

# Define timezone offset for GMT+7
gmt_plus_7 = timedelta(hours=7)

def get_current_time():
    return (datetime.utcnow() + gmt_plus_7).strftime("%H:%M:%S")

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="auto_refresh")

current_time = get_current_time()
clock_placeholder.subheader(f"Current Time: {current_time}")

@st.cache_data(ttl=5)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/1icVXJlg0MfkAwGMFN5mdiaDHP9IXvAUWXlJtluLJ4_o/edit?usp=sharing"
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=url, header=0)

        # Validate columns
        if len(df.columns) == 4:
            df.columns = ["Date", "Time", "Detection", "Image"]
        else:
            st.error(f"Dataframe has {len(df.columns)} columns, but 4 columns are expected.")
            st.stop()

        return df

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
df = load_data()

# Convert Google Drive links to direct links
def convert_gdrive_link(url):
    if "drive.google.com" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?id={file_id}"
    return url

df["Image"] = df["Image"].apply(convert_gdrive_link)

# Display the last row's detection info
if not df.empty:
    last_row = df.iloc[-1]
    last_time = last_row["Time"]
    last_detection = last_row["Detection"]
    last_image_url = last_row["Image"]

    st.subheader("🎥 Live Detection")
    st.markdown(
        f"""
        **Information**
        - **Time Captured:** {last_time}
        - **Detection Status:** {"**:red[DETECTED]**" if last_detection == 1 else "**:green[NOT DETECTED]**"}
        """
    )

    # Display the image
    st.subheader("🖼️ Latest Detection Image")
    try:
        st.image(last_image_url, caption="Latest Detection Image", use_container_width=True)
    except Exception as e:
        st.error(f"Error loading image: {e}")

    # Display the historical data table
    st.subheader("📋 Historical Data Table")
    st.dataframe(df[["Date", "Time", "Detection", "Image"]])

else:
    st.warning("No data available. Please check the Google Spreadsheet link or data format.")
