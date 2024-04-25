import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth



st.set_page_config(layout="wide")


# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetching existing data
df = conn.read(worksheet="Students", usecols=list(range(10)), ttl=5)
df = df.dropna(how="all")


with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
    config["credentials"],
    cookie_key="some_signature_key",
    cookie_name="some_cookie_name",
    cookie_expiry_days=30,
)



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


def renderAdmin(df):
    st.title("📈Visualization of the candidates")

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

    # Call the function to generate bar charts
    generate_bar_chart(df)

    # Call the function to generate pie charts
    generate_pie_charts(df)

    # Download as CSV
    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    csv = convert_df(df)

    # Display DataFrame in a collapsible expander
    with st.expander("View DataFrame"):
        st.write(df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="Student_Data.csv",
            mime="text/csv",
        )

auth(df)

