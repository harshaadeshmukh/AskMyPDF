import os
from datetime import datetime
import streamlit as st
import base64
from supabase import create_client, Client

# Supabase credentials
from config import SUPABASE_URL, SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Table name in Supabase
TABLE_NAME = "chat_history"

# -----------------------------
# Supabase History storage functions
# -----------------------------

def add_chat(question, answer, model, timestamp, pdfs, username):
    """Add a single chat entry for today's date to Supabase"""
    today = datetime.now().strftime('%Y-%m-%d')
    data = {
        "username": username,
        "question": question,
        "answer": answer,
        "model": model,
        "timestamp": timestamp,
        "pdfs": str(pdfs),
        "date": today
    }
    supabase.table(TABLE_NAME).insert(data).execute()

def get_all_history(username):
    """Fetch all chat history for a user from Supabase, grouped by date"""
    response = supabase.table(TABLE_NAME).select("*").eq("username", username).execute()
    items = response.data if response.data else []
    history = {}
    for item in items:
        date = item.get("date")
        chat = {
            "question": item.get("question"),
            "answer": item.get("answer"),
            "model": item.get("model"),
            "timestamp": item.get("timestamp"),
            "pdfs": item.get("pdfs")
        }
        if date not in history:
            history[date] = []
        history[date].append(chat)
    return history

def clear_history(username):
    """Delete all chat history for a user from Supabase"""
    supabase.table(TABLE_NAME).delete().eq("username", username).execute()




# -----------------------------
# Streamlit UI
# -----------------------------

def show_history_ui(username):
    st.markdown("""
        <h2 style='font-size:2.3rem; font-weight:700; margin-bottom:0.5rem;'>Chat Record 💬📝</h2>
    """, unsafe_allow_html=True)
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
    st.sidebar.markdown('<div style="display:flex; justify-content:center; align-items:center; margin-top:20px;">', unsafe_allow_html=True)
    delete_btn_html = f"""
        <style>
        .wide-delete-btn {{
            width: 90%;
            background: #e53e3e;
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 10px 0;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin: 0 auto;
            display: block;
        }}
        </style>
       
    """
    delete_btn_container = st.sidebar.markdown(delete_btn_html, unsafe_allow_html=True)
    # Fallback: also keep the Streamlit button for actual logic
    delete_clicked = st.sidebar.button(f'Delete chats on "{selected_date}"', key=f'delete_{selected_date}')
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    if delete_clicked:
        # Delete only chats for selected date for the user
        supabase.table(TABLE_NAME).delete().eq("username", username).eq("date", selected_date).execute()
        st.session_state["selected_date"] = None
        st.rerun()
