import streamlit as st
import pandas as pd
import os
import dropbox
from datetime import datetime, timedelta
import uuid

# Generate a unique ID for the session if it doesn't already exist
if 'unique_id' not in st.session_state:
    st.session_state.unique_id = str(uuid.uuid4())

# Get the current date
current_date = datetime.now() - timedelta(hours=5)
formatted_date = current_date.strftime("%m-%d-%y") 
day_of_week = current_date.strftime("%A")

# Define files for attendance
NAMES_FILE = "TThList.csv"
ATTENDANCE_FILE = "TThattendance" + formatted_date + ".csv"
if day_of_week in ['Monday', 'Wednesday']:
    NAMES_FILE = "MWlist.csv"
    ATTENDANCE_FILE = "MWattendance" + formatted_date + ".csv"
if day_of_week == 'Wednesday' and current_date.hour >= 18:
    NAMES_FILE = "lablist.csv"
    ATTENDANCE_FILE = "labattendance" + formatted_date + ".csv"

# Dropbox access token
DROPBOX_ACCESS_TOKEN = st.secrets['database']['dbkey']

# Upload to Dropbox
def upload_to_dropbox(file_path, dropbox_path):
    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        with open(file_path, "rb") as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
    except:
        pass

# Load names from the file
def load_names():
    if os.path.exists(NAMES_FILE):
        with open(NAMES_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    else:
        return []

# Attendance management
def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        return pd.read_csv(ATTENDANCE_FILE)
    else:
        return pd.DataFrame(columns=["Student Name", "Status", "IP_Hash"])

def save_attendance(name, status, ip_hash):
    attendance = load_attendance()
    if name in attendance['Student Name'].values:
        attendance.loc[attendance['Student Name'] == name, ['Status', 'IP_Hash']] = [status, ip_hash]
    else:
        new_data = pd.DataFrame([{"Student Name": name, "Status": status, "IP_Hash": ip_hash}])
        attendance = pd.concat([attendance, new_data], ignore_index=True)
    attendance.to_csv(ATTENDANCE_FILE, index=False)

# Check submission status
def get_submission_status(ip_hash):
    attendance = load_attendance()
    match = attendance[attendance['IP_Hash'] == ip_hash]
    if match['Status'].values[0]=='Absent':
        return 'Present'
    return match['Status'].values[0] if not match.empty else None

# App title
st.title("Attendance Form " + formatted_date)

# Auto-upload to Dropbox
if DROPBOX_ACCESS_TOKEN != '':
    upload_to_dropbox(ATTENDANCE_FILE, f"/{ATTENDANCE_FILE}")

# Unique session identifier
ip_hash = st.session_state.unique_id 

# Load student names
names_list = load_names()
if not names_list:
    st.error("No names found in the attendance sheet. Please ensure the file exists.")
else:
    st.write("Please mark your attendance below:")

    submission_status = get_submission_status(ip_hash)

    with st.form("attendance_form"):
        name = st.selectbox("Select your name", names_list)
        status = "Present" if submission_status is None else "Absent"

        submitted = st.form_submit_button("Submit")

        if submitted:
            save_attendance(name, status, ip_hash)
            st.success(f"Your attendance has been marked:  '{name}' is '{status}'!")

# Display attendance records
st.write("---")
st.subheader("Attendance Records")
attendance_df = load_attendance().drop(columns=["IP_Hash"])
attendance_df['Student Num'] = attendance_df['Student Name'].apply(lambda x: names_list.index(x) + 1 if x in names_list else None)
st.markdown(attendance_df.sort_values(by='Student Num').style.hide(axis="index").to_html(), unsafe_allow_html=True)
