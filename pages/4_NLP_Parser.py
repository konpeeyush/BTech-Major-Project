import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from streamlit_gsheets import GSheetsConnection

st.title("NLP Parsing using Similarity Coefficent Techniques on Database")
# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetching existing data
df = conn.read(worksheet="Students", usecols=list(range(10)), ttl=5)
df = df.dropna(how="all")

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


class Model:

    def __init__(self, dataset):
        self.dataset = dataset
        self.vectorizer = TfidfVectorizer(
            min_df=1, stop_words="english", lowercase=True
        )
        self.text_features = (
            self.dataset["Languages Known"]
            + " "
            + self.dataset["Soft Skills"]
            + " "
            + self.dataset["Hard Skills"]
            + " "
            + self.dataset["Co-Curricular"]
        )
        self.text_feature_vectors = self.vectorizer.fit_transform(self.text_features)

    def find(
        self,
        language,
        soft_skills,
        hard_skills,
        ex_curricular,
        min_cpi,
        min_gdpi,
        technical,
        aptitude,
        num_students,
    ):
        candidate_text = f"{language} {soft_skills} {hard_skills} {ex_curricular}"
        candidate_text_vector = self.vectorizer.transform([candidate_text]).toarray()
        similarity_scores = cosine_similarity(
            candidate_text_vector, self.text_feature_vectors
        )
        valid_indices = np.where(
            (self.dataset["CPI"] >= min_cpi)
            & (self.dataset["GDPI"] >= min_gdpi)
            & (self.dataset["Technical"] >= technical)
            & (self.dataset["Aptitude"] >= aptitude)
        )[0]

        valid_similarity_scores = similarity_scores[:, valid_indices]
        top_indices = valid_indices[
            np.argsort(valid_similarity_scores[0])[-num_students:][::-1]
        ]
        similar_students = self.dataset.iloc[top_indices][
            ["Student ID", "Student Name"]
        ].reset_index(drop=True)
        return similar_students


def renderForm(model):
    with st.form(key="student_form"):
        languages_known = st.multiselect("Languages Known:", options=LANGUAGES_KNOWN)
        soft_skills = st.multiselect("Soft Skills:", options=SOFT_SKILLS)
        hard_skills = st.multiselect("Hard Skills:", options=HARD_SKILLS)
        co_curricular = st.multiselect("Co-Curricular:", options=CO_CURRICULAR)
        min_cpi = st.slider("CPI:", min_value=6.0, max_value=10.0, step=0.15)
        min_gdpi = st.slider("GDPI:", min_value=10.0, max_value=15.0, step=0.15)
        technical = st.slider("Technical:", min_value=12.0, max_value=20.0, step=0.15)
        aptitude = st.slider("Aptitude:", min_value=12.0, max_value=20.0, step=0.15)
        num_students = st.slider(
            "Number of Candidates you want to shortlist: ",
            min_value=1,
            max_value=10,
            step=1,
        )

        submitted = st.form_submit_button(label="Submit your details")
        if submitted:
            st.success("Here are your candidates:")
            candidates = model.find(
                languages_known,
                soft_skills,
                hard_skills,
                co_curricular,
                min_cpi,
                min_gdpi,
                technical,
                aptitude,
                num_students,
            )
            st.dataframe(candidates, use_container_width=True, hide_index=True)


def csvTalk(dataset):
    model_instance = Model(dataset)
    renderForm(model_instance)


csvTalk(dataset=df)
