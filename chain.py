import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from prompt import interview_prompt, feedback_prompt
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

#groq
model1 = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    api_key=os.environ["GROQ_API_KEY"],
)

model2 = ChatOllama(
    model="minimax-m3:cloud"
)

interview_chain=interview_prompt | model1 | StrOutputParser()
feedback_chain=feedback_prompt | model2 | StrOutputParser()
