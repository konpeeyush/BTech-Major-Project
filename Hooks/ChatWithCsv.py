from langchain_experimental.agents.agent_toolkits import create_csv_agent
import os
from langchain.agents.agent_types import AgentType
from getpass import getpass
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
import streamlit as st
from dotenv import load_dotenv
import openai

openai.api_key = os.environ['OPENAI_API_KEY']

def main():
    st.header("Enter Candidate specifications")
    df = "assets/studentData.csv"
    llm = OpenAI()

    if df is not None:
        agent = create_csv_agent(
            llm, df, verbose=True, AgentType=AgentType.OPENAI_FUNCTIONS
        )

        query = st.text_input("Enter your query")
        if query is not None and query != "":
            with st.spinner(text="Loading..."):
                st.write(agent.run(query))


if __name__ == "__main__":
    main()
