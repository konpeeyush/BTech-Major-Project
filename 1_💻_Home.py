import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd


st.set_page_config(
    page_title="Parsing framework for profiling and recommendation based on resume",
    page_icon="👨‍💻",
    layout="wide"
)

st.title("Student Data Entry Form")
st.markdown("Enter the details of your relevant skills")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetching existing data
existing_data = conn.read(worksheet="Students", usecols=list(range(8)), ttl=5)
existing_data = existing_data.dropna(how="all")

# List of skills (Soft/Hard), Languages Known, CPI and GDPI scores

LANGUAGES_KNOWN = [
    "C++",
    "C",
    "HTML",
    "JAVA-SCRIPT",
    "JAVA",
    "PYTHON",
    "REACT",
    "MONGODB",
    "FLUTTER",
    "KOTLIN",
    "REACT-NATIVE",
    "LINUX",
    "C#",
]

SOFT_SKILLS = [
    "Problem Solving Skills",
    "Time Management Skills",
    "Leadership Skills",
    "Effective Communication Skills",
    "Flexible",
    "Critical Thinking Ability",
]

HARD_SKILLS = [
    "Data Structures and Algorithms",
    "Web Development",
    "Android Development",
    "Game Development",
    "Data Science",
    "Machine Learning",
    "Artificial Intelligence",
    "Deep Learning",
]

CO_CURRICULAR = ["Leetcode", "Competitive Programming", "CodeChef", "CodeForces"]

# Student Data Form
with st.form(key="student_form"):
    student_id = st.number_input(
        "Enter Your roll number*", min_value=201550000, max_value=201551000
    )
    student_name = st.text_input("Enter you Name*")
    languages_known = st.multiselect("Languages Known:", options=LANGUAGES_KNOWN)
    soft_skills = st.multiselect("Soft Skills:", options=SOFT_SKILLS)
    hard_skills = st.multiselect("Hard Skills:", options=HARD_SKILLS)
    co_curricular = st.multiselect("Co-Curricular:", options=CO_CURRICULAR)
    cpi = st.slider("Enter your CPI", 6.0, 10.0)
    gdpi = st.slider("Enter GDPI Score", 10.0, 15.0)

    # Mark mandatory fields
    st.markdown("**required*")
    submit_button = st.form_submit_button(label="Submit your details")

    # If the submit button is pressed
    if submit_button:
        if not student_id or not student_name:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        elif (
            existing_data["Student ID"].astype(str).str.contains(str(student_id)).any()
        ):
            st.warning("This roll number already exists.")
            st.stop()
        else:
            student_data = pd.DataFrame(
                [
                    {
                        "Student ID": student_id,
                        "Student Name": student_name,
                        "Languages Known": join(languages_known),
                        "Soft Skills": join(soft_skills),
                        "Hard Skills": join(hard_skills),
                        "Co-Curricular": join(co_curricular),
                        "CPI": cpi,
                        "GDPI": gdpi,
                    }
                ]
            )

            # Add the new student data to the existing data
            updated_df = pd.concat([existing_data, student_data], ignore_index=True)

            # Update Google Sheets with the new student data
            conn.update(worksheet="Students", data=updated_df)

            st.success("Student data added successfully")
