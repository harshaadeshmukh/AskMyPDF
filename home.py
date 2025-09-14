# home.py
import streamlit as st
import app  # your chatbot page
import history


# Inject global responsive font CSS
st.markdown("""
    <style>
    html, body, [class^='css'] {
        font-size: clamp(0.95rem, 2vw, 1.15rem);
    }
    h1, .stApp h1 {
        font-size: clamp(2rem, 5vw, 2.5rem);
    }
    h2, .stApp h2 {
        font-size: clamp(1.5rem, 4vw, 2rem);
    }
    h3, .stApp h3 {
        font-size: clamp(1.2rem, 3vw, 1.5rem);
    }
    .stMarkdown, .stChatMessageContent, .stExpanderContent {
        font-size: clamp(1rem, 2vw, 1.1rem);
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        font-size: clamp(1rem, 2vw, 1.1rem);
    }
    button, .stButton>button {
        font-size: clamp(1rem, 2vw, 1.1rem);
    }
    </style>
""", unsafe_allow_html=True)

# Prompt for username at app start
if "username" not in st.session_state or not st.session_state.username:

    st.markdown("""
        <style>
        .modern-welcome-card {
            background: linear-gradient(120deg, #e0e7ff 0%, #f8fafc 100%);
            padding: 2.8rem 2.5rem 2.2rem 2.5rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px #6366f133;
            max-width: 540px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .modern-welcome-icon {
            font-size: 3rem;
            color: #6366f1;
            text-shadow: 0 2px 8px #6366f133;
        }
        .modern-welcome-title {
            text-align: center;
            font-size: 2rem;
            font-weight: 800;
            color: #22223b;
            margin-bottom: 0.1rem;
            letter-spacing: 1px;
        }
        .modern-welcome-desc {
            text-align: center;
            font-size: 1.15rem;
            color: #444;
            margin-bottom: 1.7rem;
        }
        .modern-welcome-highlight {
            color: #6366f1;
            font-weight: 700;
        }
        .modern-welcome-input input {
            width: 180px !important;
            height: 28px !important;
            font-size: 1rem !important;
            padding: 4px 8px !important;
            border-radius: 8px !important;
            border: 1px solid #6366f1 !important;
            box-shadow: 0 2px 8px #6366f122;
        }
        /* Custom style for Enter button only */
        .stButton > button[data-testid="enter_btn"] {
            background: linear-gradient(90deg, #6366f1 0%, #60a5fa 100%);
            color: #fff !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 8px #6366f133;
            font-weight: 700;
            transition: background 0.2s;
        }
        .stButton > button[data-testid="enter_btn"]:hover {
            background: linear-gradient(90deg, #60a5fa 0%, #6366f1 100%);
        }
        </style>
        <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:45vh;'>
            <div class='modern-welcome-card'>
                <div class='modern-welcome-icon'>📚</div>
                <div class='modern-welcome-title'>Welcome to AskMyPDF</div>
                <div class='modern-welcome-desc'>
                    Please enter your name to personalize your chat experience.<br>
                    <span class='modern-welcome-highlight'>Your chats will be saved separately.</span>
                </div>
    """, unsafe_allow_html=True)
    # Place the textbox right after the description, inside the card
    st.markdown("<div class='modern-welcome-input' style='width:100%;max-width:160px;margin:0 auto;padding:0;'>", unsafe_allow_html=True)
    username = st.text_input("", "", key="username_input", placeholder="Please enter a unique name (e.g. John123)😊")
    enter_pressed = st.button("Enter", key="enter_btn", use_container_width=True)
    st.markdown("</div></div></div>", unsafe_allow_html=True)
    # If user enters name and presses Enter (textbox) or clicks button, go to Home
    if (enter_pressed or (username and username.strip())):
        if username and username.strip():
            st.session_state.username = username.strip()
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.markdown("<div style='width:100%;max-width:160px;padding:0;'>", unsafe_allow_html=True)
            st.warning("😅 Oops! Did you forget to enter your name? Please add a unique name to continue.")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Set page config
st.set_page_config(page_title="AskMyPDF", page_icon="📚", layout="wide")


# Sidebar Header

st.sidebar.markdown("<h2>📚 AskMyPDF</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"<span style='font-size:1.1em;'>Your AI-powered PDF assistant<br><b>Hi, </b> {st.session_state.username} 😄</span>", unsafe_allow_html=True)

# # Logout button
# if st.sidebar.button("🚪 Logout", key="logout_btn", use_container_width=True):
#     st.session_state.username = ""
#     st.session_state.page = "Home"
#     st.rerun()

# Initialize session state for navigation

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# Sidebar navigation

pages = {
    "Home": "Home",
    "Chatbot": "Chatbot",
    "History": "History"
}

for page, name in pages.items():
    if st.sidebar.button(
        page,
        key=page,
        use_container_width=True
    ):
        st.session_state.page = page

# Logout button after History
if st.sidebar.button("Logout", key="logout_btn", use_container_width=True):
    st.session_state.username = ""
    st.session_state.page = "Home"
    st.session_state.conversation_history = []  # Clear chat history on logout
    st.rerun()

# ---------------- Render pages ----------------
if st.session_state.page == "Home":
    st.markdown(
        "<h1 class='responsive-title'>🏠 Welcome to AskMyPDF</h1>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Purpose Section
    with st.container():
        st.subheader("💡 Purpose of This Chatbot")
        st.info("""
        The AI PDF Chatbot is designed to **help you interact with your PDF documents using natural language**. 
        Instead of manually searching through long PDF files, you can simply ask questions and get **instant answers**.
        """)

    # Why Use Section
    with st.container():
        st.subheader("🤔 Why Use This Chatbot?")
        col1, col2 = st.columns(2)
        col1.success("⏱ Save Time\nNo more scrolling through hundreds of pages.")
        col1.success("💬 Easy Access\nAsk questions in plain English.")
        col2.success("📂 Multiple PDFs\nUpload and query multiple PDFs at once.")
        col2.success("🎯 Accurate Responses\nUses state-of-the-art AI models.")
        st.markdown("---")

    # How it Works Section
    with st.container():
        st.subheader("⚙️ How the Chatbot Works")
        st.write("Follow these steps to get answers from your PDFs:")
        st.markdown("""
        1. **Upload PDFs** → Go to the Chatbot page and upload your documents.
        2. **Text Extraction** → Extract text from PDFs automatically.
        3. **Embeddings & Vector Store** → Convert text to embeddings for fast retrieval.
        4. **Ask Questions** → Type your queries in plain language.
        5. **AI Answer Generation** → Receive accurate answers from the AI.
        """)
        st.success("Everything happens behind the scenes in seconds!")
        st.markdown("---")

    # Tech Stack
    with st.container():
        st.subheader("🛠️ Tech Stack Behind the Chatbot")
    st.markdown("Explore the technologies powering this AI PDF Chatbot:")
    st.info("Streamlit 🚀 : Frontend & UI for uploading PDFs, navigation, and chat interface. [Learn More](https://docs.streamlit.io/)")
    st.info("LangChain 🔗 : Orchestrates AI workflow, embeddings, retrieval, and query handling. [Learn More](https://www.langchain.com/docs/)")
    st.info("HuggingFace 🧠 : Converts PDF text into embeddings for fast semantic search. [Learn More](https://huggingface.co/docs/transformers/main/en/main_classes/embeddings)")
    st.info("Stores embeddings and retrieves relevant PDF content quickly ⚡ : Vector DB [Learn More](https://faiss.ai/)")
    st.markdown("---")

    # How to Use
    with st.container():
        st.subheader("🚀 How to Use This Chatbot")
        with st.expander("Click here for detailed steps"):
            st.markdown("""
            1. Navigate to the **Chatbot** page from the sidebar.
            2. Upload one or more PDF files.
            3. Ask your questions in the input box.
            4. The chatbot will analyze your PDFs and provide answers.
            5. Optionally, download conversation history for reference.
            """)

    # Tips
    with st.container():
        st.subheader("💡 Tips for Best Results")
        col1, col2 = st.columns(2)
        col1.info("✅ Use clear and specific questions for better answers.")
        col1.info("✅ Large PDFs may take a few seconds to process.")
        col2.info("✅ Ensure text in PDFs is selectable.")
        col2.info("✅ Upload multiple PDFs to create a unified knowledge base.")

elif st.session_state.page == "Chatbot":
    app.run_chatbot(st.session_state.username)
    
elif st.session_state.page == "History":
    history.show_history_ui(st.session_state.username)
