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
    try:
        supabase.table(TABLE_NAME).insert(data).execute()
    except Exception as e:
        # Log error but don't crash the app
        print(f"⚠️ Warning: Could not save to Supabase: {str(e)}")
        # Silently continue - the chat still works, just not saved to database

def get_all_history(username):
    """Fetch all chat history for a user from Supabase, grouped by date"""
    try:
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
    except Exception as e:
        # Return empty history if connection fails
        print(f"⚠️ Warning: Could not fetch history from Supabase: {str(e)}")
        return {}

def clear_history(username):
    """Delete all chat history for a user from Supabase"""
    try:
        supabase.table(TABLE_NAME).delete().eq("username", username).execute()
    except Exception as e:
        print(f"⚠️ Warning: Could not clear history from Supabase: {str(e)}")


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

    # -----------------------------
    # Sidebar buttons (Download + Delete)
    # -----------------------------
    if chat_text:
        b64 = base64.b64encode(chat_text.encode()).decode()
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

        # Create columns for layout
        col1, col2, col3 = st.sidebar.columns([1, 6, 1])

        # Inject CSS (no glow now)
        st.sidebar.markdown(
            """
            <style>
            .stButton > button {
                font-weight: 700 !important;
                border-radius: 8px !important;
                padding: 10px 16px !important;
                transition: 0.3s !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Download button (no glow)
        with col2:
            if "download_clicked" not in st.session_state:
                st.session_state.download_clicked = False
            
            st.markdown("""
                <style>
                .stDownloadButton > button {
                    background-color: #28a745 !important;
                    color: white !important;
                    width: 100%;
                }
                </style>
                """, unsafe_allow_html=True)
                
            download_button = st.download_button(
                label="Download Chat History",
                data=chat_text,
                file_name=f"chat_{username}_{selected_date}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            if download_button:
                st.session_state.download_clicked = True
                st.sidebar.success("Chat history downloaded successfully!")

        st.sidebar.markdown("<br>", unsafe_allow_html=True)

        # Inject CSS for delete button font size
        st.sidebar.markdown(
            """
            <style>
            .stButton > button {
                font-size: 1.25rem !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        with col2:
            delete_clicked = st.button(
                f'Delete chats on {selected_date}',
                key=f'delete_{selected_date}',
                type="primary",
                use_container_width=True
            )

        if delete_clicked:
            supabase.table(TABLE_NAME).delete().eq("username", username).eq("date", selected_date).execute()
            st.sidebar.success(f"Chats for {selected_date} deleted successfully!")
            st.session_state["selected_date"] = None
            # Add a delay of 2 seconds before rerunning
            import time
            time.sleep(2)
            st.rerun()
