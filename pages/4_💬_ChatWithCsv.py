from dotenv import load_dotenv
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI

import os
import streamlit as st

load_dotenv()


def main():
    path="assets/studentData.csv"
    # path = "assets/movies.csv"
    
    st.header("Enter Candidate specifications")

    csv_file = path
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro", temperature=0.3, google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    if csv_file is not None:

        agent = create_csv_agent(llm, csv_file, verbose=True, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

        query = st.text_input("Which type of movie do you want to watch ?: ")

        if query is not None and query != "":
            with st.spinner(text="Loading..."):
                st.write(agent.run(query))


if __name__ == "__main__":
    main()
