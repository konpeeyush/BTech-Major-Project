import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

st.set_page_config(layout="wide")

# Config files to login
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
        config["credentials"],
        cookie_key="some_signature_key",
        cookie_name="some_cookie_name",
        cookie_expiry_days=30,
    )


# User has to admin then only content will render, it internally calls render Admin
def auth(df):
    authenticator.login()
    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
        renderAdmin(df)
    elif st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
    elif st.session_state["authentication_status"] is None:
        st.warning("Please enter your username and password")


# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetching existing data
df = conn.read(worksheet="Students", usecols=list(range(10)), ttl=5)
df = df.dropna(how="all")


# Function to find missing values of students whose scores have not been uploaded
def missingStudents(df):
    # Function to filter students with missing data
    def filter_students_with_missing_data(data):
        missing_data = data[
            data[["Aptitude", "Technical", "CPI", "GDPI"]].isnull().any(axis=1)
        ]
        return missing_data[["Student ID", "Student Name"]]

    if "missing_students" not in st.session_state:
        st.session_state.missing_students = None

    # Display button to show students with missing data
    if st.button("Show Students with Missing Data"):
        st.session_state.missing_students = filter_students_with_missing_data(df)
        if not st.session_state.missing_students.empty:
            st.dataframe(st.session_state.missing_students, hide_index=True)
        else:
            st.write("No students found with missing data.")

    # Form to fill missing details for selected student
    if (
        st.session_state.missing_students is not None
        and not st.session_state.missing_students.empty
    ):
        with st.form(key="admin_form"):
            # st.session_state
            selected_student = st.selectbox(
                "Select a student", st.session_state.missing_students["Student ID"]
            )
            technical = st.slider("Technical*", min_value=0.0, max_value=20.0, step=0.15)
            aptitude = st.slider("Aptitude*", min_value=0.0, max_value=20.0, step=0.15)
            cpi = st.slider("CPI*", min_value=0.0, max_value=10.0, step=0.15)
            gdpi = st.slider("GDPI*", min_value=0.0, max_value=15.0, step=0.15)

            st.markdown("**required*")
            submit_button = st.form_submit_button("Submit Your Details")

            if submit_button:
                if not technical or not aptitude or not cpi or not gdpi:
                    st.warning("Ensure all mandatory fields are filled.")
                    st.stop()
                else:
                    # Update the dataset with filled details
                    df.loc[df["Student ID"] == selected_student, "Technical"] = technical
                    df.loc[df["Student ID"] == selected_student, "Aptitude"] = aptitude
                    df.loc[df["Student ID"] == selected_student, "CPI"] = cpi
                    df.loc[df["Student ID"] == selected_student, "GDPI"] = gdpi

                    # Write the updated data back to Google Sheets
                    conn.update(worksheet="Students", data=df)
                    st.success("Data updated successfully!")


# Function to visualize to pie chart
def generate_pie_charts(df):
    # Preprocess data to count occurrences of each attribute
    def count_values(df, column_name):
        value_counts = {}
        for values in df[column_name]:
            for value in values.split(", "):
                value_counts[value] = value_counts.get(value, 0) + 1
        return value_counts

    # Create multiselect widgets for each attribute
    selected_languages = st.multiselect(
        "Select Languages Known",
        options=list(df["Languages Known"].str.split(", ").explode().unique()),
        default=list(df["Languages Known"].str.split(", ").explode().unique()),
    )

    selected_soft_skills = st.multiselect(
        "Select Soft Skills",
        options=list(df["Soft Skills"].str.split(", ").explode().unique()),
        default=list(df["Soft Skills"].str.split(", ").explode().unique()),
    )

    selected_hard_skills = st.multiselect(
        "Select Hard Skills",
        options=list(df["Hard Skills"].str.split(", ").explode().unique()),
        default=list(df["Hard Skills"].str.split(", ").explode().unique()),
    )

    selected_co_curricular = st.multiselect(
        "Select Co-Curricular Activities",
        options=list(df["Co-Curricular"].str.split(", ").explode().unique()),
        default=list(df["Co-Curricular"].str.split(", ").explode().unique()),
    )

    # Filter DataFrame based on selected values
    filtered_df = df[
        df["Languages Known"].apply(
            lambda x: any(language in x for language in selected_languages)
        )
        & df["Soft Skills"].apply(
            lambda x: any(skill in x for skill in selected_soft_skills)
        )
        & df["Hard Skills"].apply(
            lambda x: any(skill in x for skill in selected_hard_skills)
        )
        & df["Co-Curricular"].apply(
            lambda x: any(activity in x for activity in selected_co_curricular)
        )
    ]

    # Count occurrences of each attribute in filtered DataFrame
    language_counts = count_values(filtered_df, "Languages Known")
    soft_skill_counts = count_values(filtered_df, "Soft Skills")
    hard_skill_counts = count_values(filtered_df, "Hard Skills")
    co_curricular_counts = count_values(filtered_df, "Co-Curricular")

    # Create Plotly Pie Charts for each attribute
    languages_fig = px.pie(
        names=list(language_counts.keys()),
        values=list(language_counts.values()),
        title="Languages Known",
    )

    soft_skill_fig = px.pie(
        names=list(soft_skill_counts.keys()),
        values=list(soft_skill_counts.values()),
        title="Soft Skills",
    )

    hard_skill_fig = px.pie(
        names=list(hard_skill_counts.keys()),
        values=list(hard_skill_counts.values()),
        title="Hard Skills",
    )

    co_curricular_fig = px.pie(
        names=list(co_curricular_counts.keys()),
        values=list(co_curricular_counts.values()),
        title="Co-Curricular Activities",
    )

    # Display the pie charts in separate columns
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(languages_fig)
    with col1:
        st.plotly_chart(soft_skill_fig)
    with col2:
        st.plotly_chart(hard_skill_fig)
    with col2:
        st.plotly_chart(co_curricular_fig)


# Function to visualize bar chart
def generate_bar_chart(df):

    def cpi_chart(df):
        # Create slider for CPI range
        min_cpi = df["CPI"].min()
        max_cpi = df["CPI"].max()
        selected_cpi_range = st.slider(
            "Select CPI Range", min_cpi, max_cpi, (min_cpi, max_cpi), step=0.15
        )

        # Filter DataFrame based on selected CPI range
        filtered_df = df[
            (df["CPI"] >= selected_cpi_range[0]) & (df["CPI"] <= selected_cpi_range[1])
        ]

        # Create bar chart for CPI
        cpi_chart = px.bar(
            filtered_df,
            x="Student Name",
            y="CPI",
            title="CPI Distribution",
            labels={"CPI": "CPI"},
        )

        st.plotly_chart(cpi_chart, use_container_width=True)

    cpi_chart(df)

    def gdpi_chart(df):
        # Create slider for GDPI range
        min_gdpi = df["GDPI"].min()
        max_gdpi = df["GDPI"].max()
        selected_gdpi_range = st.slider(
            "Select GDPI Range", min_gdpi, max_gdpi, (min_gdpi, max_gdpi), step=0.15
        )

        # Filter DataFrame based on selected GDPI range
        filtered_df_gdpi = df[
            (df["GDPI"] >= selected_gdpi_range[0])
            & (df["GDPI"] <= selected_gdpi_range[1])
        ]

        # Create bar chart for GDPI
        gdpi_chart = px.bar(
            filtered_df_gdpi,
            x="Student Name",
            y="GDPI",
            title="GDPI Distribution",
            labels={"GDPI": "GDPI"},
        )
        st.plotly_chart(gdpi_chart, use_container_width=True)

    gdpi_chart(df)


def renderAdmin(df):
    st.header(
        "Enter the values of the students whose scores have not being uploaded yet",
        divider="rainbow",
    )
    with st.expander("Look For Details"):
        missingStudents(df)

    st.header("Visualization of Student Skillset, CPI and GDPI", divider="rainbow")
    with st.expander("Visualize CPI and GDPI Scores in your University"):
        generate_bar_chart(df)

    with st.expander("Visualize skillset in your University"):
        generate_pie_charts(df)

    # Download as CSV
    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    csv = convert_df(df)
    with st.expander("View DataFrame"):
        st.dataframe(df, hide_index=True)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="Student_Data.csv",
            mime="text/csv",
        )


auth(df)
