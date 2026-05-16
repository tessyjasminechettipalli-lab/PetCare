import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date

st.set_page_config(
    page_title="Pet Care Reminder System",
    page_icon="🐾",
    layout="wide"
)

st.markdown("""
<style>

/* Main background */
.stApp {
    background: #f8fafc;
            }

/* Title */
h1 {
    color: #4c1d95 !important;
    text-align: center;
    font-size: 50px !important;
    font-weight: bold;
    background: linear-gradient(to right, #7c3aed, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
}
            h2, h3, label,p {
            color:#111827 !important;
            font-weight:600;
            }

/* Subheadings */
h2, h3 {
    color: #ec4899;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #7c3aed, #ec4899);
    padding-top: 20px;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: white;
    font-size: 16px;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(to right, #7c3aed, #ec4899);
    color: white;
    border-radius: 12px;
    border: none;
    height: 3em;
    font-size: 17px;
    font-weight: bold;
    width: 100%;
    transition: 0.3s;
}

/* Button hover */
div.stButton > button:hover {
    transform: scale(1.03);
    background: linear-gradient(to right, #6d28d9, #db2777);
}

/* Input boxes */
.stTextInput > div > div > input,
.stNumberInput input,
.stDateInput input,
textarea {
    border-radius: 10px !important;
    border: 2px solid #d8b4fe !important;
    padding: 10px !important;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px !important;
    border: 2px solid #d8b4fe !important;
}

/* Metrics cards */
[data-testid="metric-container"] {
    background: white;
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    border-left: 8px solid #7c3aed;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
}

/* Image cards */
img {
    border-radius: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
}

/* Cards effect */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Success message */
.stSuccess {
    border-radius: 10px;
}

/* Warning */
.stWarning {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# DATABASE CONNECTION
conn = sqlite3.connect('petcare.db', check_same_thread=False)
c = conn.cursor()

# CREATE TABLES
c.execute('''
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    age INTEGER,
    owner TEXT,
    photo TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_name TEXT,
    reminder_type TEXT,
    reminder_date TEXT
)
''')

conn.commit()

# TITLE
st.title("🐾 Pet Care Reminder System")

# SIDEBAR MENU
menu = [
    "Dashboard",
    "Add Pet",
    "View Pets",
    "Search Pet",
    "Delete Pet",
    "Add Reminder",
    "View Reminders"
]

choice = st.sidebar.selectbox("Menu", menu)

# DASHBOARD
if choice == "Dashboard":
    st.subheader("Dashboard")
    pet_count = c.execute("SELECT COUNT(*) FROM pets").fetchone()[0]
    reminder_count = c.execute("SELECT COUNT(*) FROM reminders").fetchone()[0]

    col1, col2 = st.columns(2)
    col1.metric("Total Pets", pet_count)
    col2.metric("Total Reminders", reminder_count)

# ADD PET
elif choice == "Add Pet":
    st.subheader("Add New Pet")
    name = st.text_input("Pet Name")
    pet_type = st.text_input("Pet Type")
    age = st.number_input("Pet Age", 0, 50)
    owner = st.text_input("Owner Name")
    photo = st.file_uploader("Upload Pet Photo", type=["jpg", "png", "jpeg"])

    if st.button("Save Pet"):
        photo_path = ""
        if photo is not None:
            if not os.path.exists("photos"):
                os.makedirs("photos")
            photo_path = f"photos/{photo.name}"
            with open(photo_path, "wb") as f:
                f.write(photo.getbuffer())

        c.execute('''
            INSERT INTO pets(name, type, age, owner, photo)
            VALUES (?, ?, ?, ?, ?)
            ''', (name, pet_type, age, owner, photo_path))
        conn.commit()
        st.success("Pet Added Successfully!")

# VIEW PETS
elif choice == "View Pets":
    st.subheader("All Pets")
    data = pd.read_sql_query("SELECT * FROM pets", conn)

    if data.empty:
        st.warning("No pets added yet.")
    else:
        for index, row in data.iterrows():
            st.write(f"### 🐶 {row['name']}")
            st.write(f"Type: {row['type']}")
            st.write(f"Age: {row['age']}")
            st.write(f"Owner: {row['owner']}")
            if row['photo'] != "":
                st.image(row['photo'], width=200)
            st.write("---")

# SEARCH PET
elif choice == "Search Pet":
    st.subheader("Search Pet")
    search_name = st.text_input("Enter Pet Name")

    if st.button("Search"):
        query = 'SELECT * FROM pets WHERE name LIKE ?'
        result = pd.read_sql_query(query, conn, params=(f"%{search_name}%",))

        if result.empty:
            st.error("No pet found.")
        else:
            for index, row in result.iterrows():
                st.write(f"### 🐾 {row['name']}")
                st.write(f"Type: {row['type']}")
                st.write(f"Age: {row['age']}")
                st.write(f"Owner: {row['owner']}")
                if row['photo'] != "":
                    st.image(row['photo'], width=200)

# DELETE PET
elif choice == "Delete Pet":
    st.subheader("Delete Pet")
    pets = pd.read_sql_query("SELECT name FROM pets", conn)
    pet_names = pets['name'].tolist()

    selected_pet = st.selectbox("Select Pet", pet_names)

    if st.button("Delete"):
        c.execute("DELETE FROM pets WHERE name = ?", (selected_pet,))
        conn.commit()
        st.success("Pet Deleted Successfully!")
        st.rerun()

# ADD REMINDER
elif choice == "Add Reminder":
    st.subheader("Add Reminder")
    pet_name = st.text_input("Pet Name")
    reminder_type = st.selectbox("Reminder Type", ["Feeding", "Vaccination", "Vet Visit", "Medicine"])
    reminder_date = st.date_input("Reminder Date")

    if st.button("Save Reminder"):
        c.execute('''
            INSERT INTO reminders(pet_name, reminder_type, reminder_date)
            VALUES (?, ?, ?)
            ''', (pet_name, reminder_type, str(reminder_date)))
        conn.commit()
        st.success("Reminder Added Successfully!")

# VIEW & DELETE REMINDERS
elif choice == "View Reminders":
    st.subheader("All Reminders")
    
    today = str(date.today())
    
    # Check for today's reminders
    today_reminders = pd.read_sql_query("SELECT * FROM reminders WHERE reminder_date = ?", conn, params=(today,))
    if not today_reminders.empty:
        st.warning("⚠️ You have reminders for today!")
        st.dataframe(today_reminders, use_container_width=True)

    # Fetch all reminders
    reminders = pd.read_sql_query("SELECT * FROM reminders", conn)

    if reminders.empty:
        st.warning("No reminders added.")
    else:
        st.write("### Upcoming & Past Reminders")
        st.dataframe(reminders, use_container_width=True)
        
        st.write("---")
        st.write("### 🗑️ Delete a Reminder")
        
        # Create a clean label format for the selectbox map: "ID: Pet Name (Type) - Date"
        reminders['dropdown_label'] = reminders.apply(
            lambda r: f"ID {r['id']}: {r['pet_name']} ({r['reminder_type']}) on {r['reminder_date']}", axis=1
        )
        
        selected_reminder_label = st.selectbox("Select Reminder to Delete", reminders['dropdown_label'].tolist())
        
        # Extract the original database ID from the chosen string label
        selected_id = int(selected_reminder_label.split(":")[0].replace("ID ", ""))
        
        if st.button("Delete Reminder"):
            c.execute("DELETE FROM reminders WHERE id = ?", (selected_id,))
            conn.commit()
            st.success("Reminder Deleted Successfully!")
            st.rerun()  # Refreshes the app state to instantly update the dataframes