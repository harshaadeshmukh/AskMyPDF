import os
import json
from datetime import datetime
import streamlit as st
import asyncio
import nest_asyncio
import base64

HISTORY_FILE = "chat_history.json"

# Fix asyncio loop issue for Streamlit
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
nest_asyncio.apply()

# -----------------------------
# History storage functions
# -----------------------------

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_chat(question, answer, model, timestamp, pdfs):
    """Add a single chat entry for today's date"""
    today = datetime.now().strftime('%Y-%m-%d')
    history = load_history()
    if today not in history:
        history[today] = []
    chat = {
        "question": question,
        "answer": answer,
        "model": model,
        "timestamp": timestamp,
        "pdfs": pdfs
    }
    history[today].append(chat)
    save_history(history)

def get_all_history():
    return load_history()

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

# -----------------------------
# Streamlit UI
# -----------------------------

def show_history_ui():
    st.title("🕑 Chat History Browser")
    history = get_all_history()
    if not history:
        st.info("No chat history found.")
        return

    # Pick a date from main page, default to latest
    dates = list(history.keys())
    if not dates:
        st.info("No chat dates found.")
        return
    selected_date = st.selectbox("📅 Choose a chat date:", dates, index=len(dates)-1)

    # Display chats
    chats = history[selected_date]
    st.markdown(f"### Chats for {selected_date}")

    chat_text = ""
    for chat in chats:
        st.markdown(f"**Q:** {chat['question']}")
        st.markdown(f"**A:** {chat['answer']}")
        st.caption(f"Model: {chat['model']} | Time: {chat['timestamp']} | PDFs: {chat['pdfs']}")
        st.markdown("---")
        chat_text += f"Question: {chat['question']}\nAnswer: {chat['answer']}\nModel: {chat['model']}\nTimestamp: {chat['timestamp']}\nPDFs: {chat['pdfs']}\n{'-'*50}\n"

    # Download selected date’s chats (button in sidebar)
    if chat_text:
        b64 = base64.b64encode(chat_text.encode()).decode()
        st.sidebar.markdown(
            f'<div style="text-align:center;">'
            f'<a href="data:file/txt;base64,{b64}" download="chat_{selected_date}.txt">'
            f'<button style="background-color:#888; color:#fff;margin-top :20px;border:none; padding:8px 16px; border-radius:7px; cursor:pointer; font-size:16px;">Download This Date</button></a>'
            f'</div>',
            unsafe_allow_html=True
        )

