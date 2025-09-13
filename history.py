# history.py
import os
import json
from datetime import datetime
import streamlit as st
import asyncio
import nest_asyncio

HISTORY_FILE = "chat_history.json"

try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
nest_asyncio.apply()


# Structure: {date: [ [session1], [session2], ... ] }

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def start_new_session():
    """Start a new chat session for today, returns session_id (index in today's list)"""
    today = datetime.now().strftime('%Y-%m-%d')
    history = load_history()
    if today not in history:
        history[today] = []
    history[today].append([])  # new session
    save_history(history)
    return today, len(history[today]) - 1

def add_chat_to_session(question, answer, model, timestamp, pdfs, date=None, session_id=None):
    """Add a chat to a specific session (date, session_id)"""
    if date is None or session_id is None:
        date, session_id = start_new_session()
    history = load_history()
    chat = {
        "question": question,
        "answer": answer,
        "model": model,
        "timestamp": timestamp,
        "pdfs": pdfs
    }
    # Ensure date/session exists
    if date not in history:
        history[date] = []
    while len(history[date]) <= session_id:
        history[date].append([])
    history[date][session_id].append(chat)
    save_history(history)

def get_all_history():
    """Return all history grouped by date and session"""
    return load_history()

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

# Streamlit UI for browsing chat history

def show_history_ui():
    st.title("🕑 Chat History Browser")
    history = get_all_history()
    if not history:
        st.info("No chat history found.")
        return
    dates = list(history.keys())
    selected_date = st.selectbox("Select a date:", dates)
    sessions = history[selected_date]
    session_options = [f"Session {i+1} ({len(session)} chats)" for i, session in enumerate(sessions)]
    selected_session_idx = st.selectbox("Select a session:", range(len(sessions)), format_func=lambda i: session_options[i])
    selected_session = sessions[selected_session_idx]
    st.markdown(f"### Chats for {selected_date}, Session {selected_session_idx+1}")
    for chat in selected_session:
        st.markdown(f"**Q:** {chat['question']}")
        st.markdown(f"**A:** {chat['answer']}")
        st.caption(f"Model: {chat['model']} | Time: {chat['timestamp']} | PDFs: {chat['pdfs']}")
        st.markdown("---")

# To use: call show_history_ui() from your main app or sidebar
