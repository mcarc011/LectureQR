import streamlit as st
import pandas as pd
import os
import hashlib
import dropbox
from datetime import datetime

# Get the current date
current_date = datetime.now()

# Format the date as mm-dd-yy
formatted_date = current_date.strftime("%m-%d-%y")
day_of_week = current_date.strftime("%A")


# Define files for attendance
ATTENDANCE_FILE = "attendance"+formatted_date+".csv"
if day_of_week in ['Monday','Wednesday']:
    NAMES_FILE = "MWlist.csv"
NAMES_FILE = "MWlist.csv"


# Add your Dropbox access token
DROPBOX_ACCESS_TOKEN = st.secrets['database']['dbkey']

# Upload the file to Dropbox
def upload_to_dropbox(file_path, dropbox_path):
    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        with open(file_path, "rb") as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
        st.success(f"Attendance file uploaded to Dropbox: {dropbox_path}")
    except Exception as e:
        st.error(f"Failed to upload to Dropbox: {e}")


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
        return pd.DataFrame(columns=["Name", "Status", "IP_Hash"])

def save_attendance(name, status, ip_hash):
    attendance = load_attendance()
    new_data = pd.DataFrame([{"Name": name, "Status": status, "IP_Hash": ip_hash}])
    attendance = pd.concat([attendance, new_data], ignore_index=True)
    attendance.to_csv(ATTENDANCE_FILE, index=False)

    # Automatically upload to Dropbox
    upload_to_dropbox(ATTENDANCE_FILE, f"/{ATTENDANCE_FILE}")


def is_duplicate_submission(ip_hash):
    attendance = load_attendance()
    return ip_hash in attendance["IP_Hash"].values

# App title
st.title("Attendance Form")

# Get the user IP (simulated by session state)
ip_address = st.query_params.get("ip", ["unknown"])[0]
ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()

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
            name = st.selectbox("Select your name", names_list)
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
st.dataframe(attendance_df)
