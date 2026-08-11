from pathlib import Path
from langchain_community.chat_message_histories import SQLChatMessageHistory


# Deciding where the SQLITE file lives
DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "interview_history.db"
DATA_DIR.mkdir(exist_ok=True)

# check the user history
def get_session_history(session_id: str):
    # Reconnects to the same file/session_id each call, so history persists across restarts insted
    # of just living in the momory
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=f"sqlite:///{DB_PATH.as_posix()}",
    )