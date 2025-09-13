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

# Set page config
st.set_page_config(page_title="AskMyPDF", page_icon="📚", layout="wide")

# Sidebar styling
st.markdown(
    """
    <style>
    /* Sidebar background */
    [data-testid="stSidebar"] {
        color: white;
        padding-top: 20px;
    }

    /* Sidebar title */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white;
    }

    /* Sidebar buttons (navigation) */
    .sidebar-btn {
        display: block;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 500;
        color: white;
        background-color: transparent;
        border: 1px solid #374151; /* Dark border */
        transition: 0.3s;
    }

    /* Hover effect */
    .sidebar-btn:hover {
        background-color: #1F2937; /* Dark Gray */
        border: 1px solid #4B5563; /* Slightly lighter border on hover */
    }

    /* Active button */
    .active-btn {
        background-color: #000000; /* Black */
        font-weight: 600;
        border: 1px solid #6B7280; /* Highlighted dark border */
    }

    /* Responsive Title */
    .responsive-title {
        text-align: center;
        color: white;
        font-size: 2.1rem; /* default desktop size */
        font-weight: bold;
    }
    @media (max-width: 705px) {
        .responsive-title {
            font-size: 1.5rem; /* tablets */
            padding: 0 10px;
            word-wrap: break-word;
        }
    }
    @media (max-width: 400px) {
        .responsive-title {
            font-size: 1.0rem; /* phones */
            padding: 0 5px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Header
st.sidebar.markdown("<h2>📚 AskMyPDF</h2>", unsafe_allow_html=True)
st.sidebar.caption("Your AI-powered PDF assistant")

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# Sidebar navigation

pages = {
    "🏠 Home": "",
    "💬 Chatbot": "",
    "📜 History": ""
}


for icon, name in pages.items():
    if st.sidebar.button(
        f"{icon} {name}",
        key=icon,
        use_container_width=True
    ):
        st.session_state.page = icon

# ---------------- Render pages ----------------
if st.session_state.page == "🏠 Home":
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

elif st.session_state.page == "💬 Chatbot":
    app.run_chatbot()
    
elif st.session_state.page == "📜 History":
    history.show_history_ui()