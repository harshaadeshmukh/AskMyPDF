import os
import json
from datetime import datetime
import streamlit as st
import asyncio
import nest_asyncio
import base64


def get_history_file(username):
    safe_name = "_".join(username.strip().split()).lower()
    return os.path.join("history_json", f"chat_history_{safe_name}.json")

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


def load_history(username):
    HISTORY_FILE = get_history_file(username)
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history, username):
    HISTORY_FILE = get_history_file(username)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def add_chat(question, answer, model, timestamp, pdfs, username):
    """Add a single chat entry for today's date"""
    today = datetime.now().strftime('%Y-%m-%d')
    history = load_history(username)
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
    save_history(history, username)


def get_all_history(username):
    return load_history(username)


def clear_history(username):
    HISTORY_FILE = get_history_file(username)
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

# -----------------------------
# Streamlit UI
# -----------------------------


def show_history_ui(username):

    st.title("🕑 Chat History Browser")
    history = get_all_history(username)
    if not history:
        st.info("No chat history found.")
        return

    # Order dates chronologically
    try:
        dates = sorted(history.keys(), key=lambda d: datetime.strptime(d, "%Y-%m-%d"))
    except Exception:
        dates = sorted(history.keys())
    if not dates:
        st.info("No chat dates found.")
        return
    # Use session_state to persist selected date
    if "selected_date" not in st.session_state or st.session_state["selected_date"] not in dates:
        st.session_state["selected_date"] = dates[-1]
    selected_date = st.selectbox("📅 Choose a chat date:", dates, index=dates.index(st.session_state["selected_date"]))
    st.session_state["selected_date"] = selected_date

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
            f'<a href="data:file/txt;base64,{b64}" download="chat_{username}_{selected_date}.txt">'
                f'<button style="background-color:#888; background-color:green;margin-top :20px;border:none; padding:8px 16px; border-radius:7px; cursor:pointer; font-size:16px;margin-bottom:1px;">Download Chat History</button></a>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Sidebar delete button (centered visually, Streamlit logic)
    st.sidebar.markdown('<div style="text-align:center; margin-top:20px;  border-radius:7px; padding:4px;">', unsafe_allow_html=True)
    delete_clicked = st.sidebar.button(f'Delete chat on "{selected_date}"', key=f'delete_{selected_date}')
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    if delete_clicked:
        history.pop(selected_date, None)
        save_history(history, username)
        dates = sorted(history.keys(), key=lambda d: datetime.strptime(d, "%Y-%m-%d")) if history else []
        if dates:
            st.session_state["selected_date"] = dates[-1]
        else:
            st.session_state["selected_date"] = None
        st.rerun()
