import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import io
import base64
import matplotlib.pyplot as plt

# Set up the Streamlit page configuration
st.set_page_config(page_title="KONTOL", page_icon="🚬")

# Title and description
st.title("Illegal Parking")
st.subheader("📘 Capstone Project Group 24")
st.write(
    """
    This app connects to a Google Spreadsheet and displays real-time data to help monitor smoking activity.
    You can analyze detection trends, view historical metrics, and examine images for improved insights.
    """
)

# Real-time clock
st.subheader("⏰ Current Time (UTC+7)", divider="gray")
clock_placeholder = st.empty()

# Define timezone offset for GMT+7
gmt_plus_7 = timedelta(hours=7)

# Function to get current time in GMT+7
def get_current_time():
    return (datetime.utcnow() + gmt_plus_7).strftime("%H:%M:%S")

# Cache the data loading function with a TTL of 5 seconds
@st.cache_data(ttl=5)
def load_data():
    # Create a connection to Google Sheets
    url = "https://docs.google.com/spreadsheets/d/1bcept49fnUiGc3s5ou_68MLuwhhzhNUNvNMANesQ1Zk/edit?usp=sharing"
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, header=1)
    df.columns = ["Date", "Time", "Detection"]
    df = df.dropna(axis=1, how='all')
    return df

# Load and process the data
df = load_data()

if not df.empty:
    # Last row processing
    last_row = df.iloc[-1]
    last_time = last_row.get("Time")
    last_detection = last_row.get("Detection")
#    last_imdata = last_row.get("Image Data")

    # Live Detection Section
    st.subheader("🎥 Live Detection", divider="gray")
    st.markdown(
        f"""
        **Information**
        - **Time Taken:** {last_time}
        - **Detection Status:** {"**:red[DETECTED]**" if last_detection == 1 else "**:green[NOT DETECTED]**"}
        """
    )

    # Display the detected image
    if last_imdata:
        try:
            image_data = base64.b64decode(last_imdata)
            image = Image.open(io.BytesIO(image_data))
            st.image(image, use_column_width=True)
        except Exception as e:
            st.error(f"Failed to decode or display image: {e}")

    # Metrics
    total_images = len(df)
    total_detections = df["Detection"].sum()
    detection_rate = (total_detections / total_images) * 100 if total_images > 0 else 0
    avg_detections_per_hour = total_detections / 24 if total_detections > 0 else 0

    # Display Metrics and Pie Chart
    st.subheader("📊 Historical Metrics and Analysis", divider="gray")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            **Historical Metrics**
            - Total Captured Images: {total_images}
            - Total Detections: {total_detections}
            - Detection Rate: {detection_rate:.2f}%
            - Average Detections Per Hour: {avg_detections_per_hour:.2f}
            """
        )

    with col2:
        fig1, ax1 = plt.subplots()
        labels = ['Detected', 'Not Detected']
        sizes = [total_detections, total_images - total_detections]
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)

    # Cumulative Detection Rate Graph
    st.subheader("📈 Cumulative Detection Rate Over Time", divider="gray")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    time_series = pd.to_datetime(df["Time"], format="%H:%M:%S")
    detection_cumsum = df["Detection"].cumsum() / (df.index + 1) * 100
    ax2.plot(time_series, detection_cumsum, label="Cumulative Detection Rate", color="blue")
    ax2.set_title("Cumulative Detection Rate Over Time")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Detection Rate (%)")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

    # Display Historical Data Table
    st.subheader("📋 Historical Data Table", divider="gray")
    st.dataframe(df[["Date", "Time", "Detection"]])

# Main loop for clock update and timed rerun
start_time = time.time()  # Record the start time

while True:
    current_time = get_current_time()
    clock_placeholder.subheader(f"{current_time}")
    time.sleep(1)
    if time.time() - start_time >= 5:
        st.cache_data.clear()
        st.rerun()