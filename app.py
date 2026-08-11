import streamlit as st

from dotenv import load_dotenv
load_dotenv()

from langchain_core.runnables.history import RunnableWithMessageHistory
from chain import interview_chain, feedback_chain
from memory_histroy import get_session_history
from prompt import interview_prompt,feedback_prompt


# bolts the memory onto interview_chain: auto-load history, auto-saves the que+ans
interview_with_memory = RunnableWithMessageHistory(
    interview_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# flattens saved history into 1 plain-text block for feedback_chain
def format_transcript(session_id: str) -> str:
    history=get_session_history(session_id)
    lines=[]
    for msg in history.messages:
        speaker="interviewer" if msg.type=="ai" else "Candidate"
        lines.append(f"{speaker}: {msg.content}")
    return "\n".join(lines)


# sets the tab title & icon & the page title
st.set_page_config(page_title="AI Mock Interview Coach", page_icon="🎤")
st.title("🎤 AI Mock Interview Coach")

# sidebar
with st.sidebar:
    name = st.text_input("Your name (this is your session ID)")
    role = st.text_input("Role you're interviewing for", placeholder="e.g. Backend Developer")
    start_clicked = st.button("Start / Resume Interview")


# remembers the click across reruns
if "started" not in st.session_state:
    st.session_state.started = False
if start_clicked and name and role:
    st.session_state.started = True


# the gate - nothing below this runs until Start has been clicked
if not st.session_state.started:
    st.info("Enter your name and role, then click 'Start / Resume Interview")
    st.stop()


# tells langchain which student's session to read/write, & chceks it
config = {"configurable": {"session_id": name}}
history = get_session_history(name)
    
# only brand-new session - fires the very first que
if len(history.messages) == 0:
    with st.spinner("Starting interview..."):
        interview_with_memory.invoke(
            {"role": role, "input": "Start the interview."}, config=config
        )


# redraws the entire saved conversation, fresh, every single time
for msg in get_session_history(name).messages:
    with st.chat_message("assistant" if msg.type == "ai" else "user"):
        st.write(msg.content)


# interview-ended: second remembered flag
if "interview_ended" not in st.session_state:
    st.session_state.interview_ended = False


if not st.session_state.interview_ended:
    # capture the typed input , saves it, then restarts immediately
    answer = st.chat_input("Type your answer...")
    if answer:
        interview_with_memory.invoke({"role": role, "input": answer}, config=config)
        st.rerun()
    # same session_state + rerun -> ending the interview
    if st.button("End Interview & Get Feedback"):
        st.session_state.interview_ended=True
        st.rerun()


# feedack report
else:
    st.subheader("Feedback Report")
    with st.spinner("Generating feedback..."):
        transcript = format_transcript(name)
        report = feedback_chain.invoke({"role": role, "transcript": transcript})
    st.write(report)