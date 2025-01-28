import streamlit as st
import pandas as pd
import os
import hashlib
import dropbox
from datetime import datetime
import uuid

# Generate a unique ID for the session if it doesn't already exist
if 'unique_id' not in st.session_state:
    # Generate a unique ID based on UUID
    st.session_state.unique_id = str(uuid.uuid4())

# Get the current date
current_date = datetime.now()

# Format the date as mm-dd-yy
formatted_date = current_date.strftime("%m-%d-%y") 
day_of_week = current_date.strftime("%A")
st.write(current_date)
# Define files for attendance
NAMES_FILE = "TThList.csv"
ATTENDANCE_FILE = "TThattendance"+formatted_date+".csv"
if day_of_week in ['Monday','Wednesday']:
    NAMES_FILE = "MWlist.csv"
    ATTENDANCE_FILE = "MWattendance"+formatted_date+".csv"
if day_of_week=='Wednesday' and current_date.hour >= 18:
    NAMES_FILE = "lablist.csv"
    ATTENDANCE_FILE = "labattendance"+formatted_date+".csv"

# Add your Dropbox access token
DROPBOX_ACCESS_TOKEN = st.secrets['database']['dbkey']

# Upload the file to Dropbox
def upload_to_dropbox(file_path, dropbox_path):
    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        with open(file_path, "rb") as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
    except:
        pass


# Load names from the text file
def load_names():
    if os.path.exists(NAMES_FILE):
        with open(NAMES_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    else:
        return []

# Initialize the app
def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        return pd.read_csv(ATTENDANCE_FILE)
    else:
        return pd.DataFrame(columns=["Student Name", "Status", "IP_Hash"])

def save_attendance(name, status, ip_hash):
    attendance = load_attendance()
    new_data = pd.DataFrame([{"Student Name": name, "Status": status, "IP_Hash": ip_hash}])
    attendance = pd.concat([attendance, new_data], ignore_index=True)
    attendance.to_csv(ATTENDANCE_FILE, index=False)

    # Automatically upload to Dropbox
    upload_to_dropbox(ATTENDANCE_FILE, f"/{ATTENDANCE_FILE}")


def is_duplicate_submission(ip_hash):
    attendance = load_attendance()
    return ip_hash in attendance["IP_Hash"].values

# App title
st.title("Attendance Form " + formatted_date)

# Get the user IP (simulated by session state)
ip_hash = st.session_state.unique_id 

# Load names for the dropdown
names_list = load_names()
if not names_list:
    st.error("No names found in the attendance sheet. Please ensure 'names.txt' exists and contains names.")
else:
    # Attendance form
    st.write("Please mark your attendance below:")

    if is_duplicate_submission(ip_hash):
        st.warning("You have already submitted your attendance.")
    else:
        with st.form("attendance_form"):
            attendance = load_attendance()
            name = st.selectbox("Select your name", [ni for ni in names_list if ni not in attendance['Student Name'].values])
            status = "Present"

            submitted = st.form_submit_button("Submit")

            if submitted:
                if name and status:
                    save_attendance(name, status, ip_hash)
                    st.success("Your attendance has been recorded!")
                else:
                    st.error("Please fill out all fields.")

# Show attendance records (optional)
st.write("---")
st.subheader("Attendance Records")
attendance_df = load_attendance().drop(columns=["IP_Hash"])
attendance_df['Student Num'] = [names_list.index(ni)+1 for ni in attendance_df['Student Name']]
st.markdown(attendance_df.sort_values(by='Student Num').style.hide(axis="index").to_html(), unsafe_allow_html=True)