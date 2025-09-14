import asyncio
import nest_asyncio
import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import base64
from datetime import datetime
import config
import random
# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

from history import add_chat  # Add this import at the top

# ---------------- Setup asyncio for Streamlit ----------------
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
nest_asyncio.apply()


def handle_special_keywords(user_question, conversation_history):
    """
    Handle special keyword responses with personality and creativity
    Returns (should_handle, response) tuple
    """
    user_question_lower = user_question.lower()
    

    # Only keep 'hi' and 'thank you' special keywords
    hello_keywords = ["hi" , "hello", "hey" , "greetings", "good morning", "good afternoon", "good evening"]
    hello_responses = [
        "👋 Hi there! Ready to dive into some PDF magic? What would you like to explore today?",
        "✨ Hi! Consider me your personal PDF whisperer. What would you like to know?"
    ]
    
    bye_keywords = ["bye", "by"]
    bye_responses = [
        "👋 Bye! Hope to chat with you again soon. Keep exploring those PDFs!",
        "✨ Goodbye! May your PDF adventures be ever fruitful. See you next time!"
    ]

    gratitude_keywords = ["thank you" , "thanks", "thx", "thankful", "appreciate it"]
    gratitude_responses = [
        "😄 My pleasure! That's what I'm here for - making your PDF journey smoother!",
        "🙏🏻 You're very welcome! Happy to help a fellow knowledge explorer!",
        "✨ Anytime! Your curiosity makes my circuits happy!",
        "🌟 Glad I could help! Keep those questions coming!",
        "💫 You're so welcome! Together we're unlocking document mysteries!"
    ]

    if any(keyword in user_question_lower for keyword in hello_keywords):
        return True, random.choice(hello_responses)
    elif any(keyword in user_question_lower for keyword in gratitude_keywords):
        return True, random.choice(gratitude_responses)
    elif any(keyword in user_question_lower for keyword in bye_keywords):
        return True, random.choice(bye_responses)
    return False, None

# ---------------- Google API Key with fallback ----------------
def get_api_key():
    """Get API key from config or user input"""
    try:
        # Try to get from config first
        api_key = config.GOOGLE_API_KEY
        if api_key and api_key.strip():
            return api_key
    except (AttributeError, ImportError):
        pass
    
    # If config key doesn't exist or is empty, use session state
    return st.session_state.get('user_api_key', '')

def validate_api_key(api_key):
    """Basic validation for Google API key format"""
    if not api_key or not api_key.strip():
        return False
    # Google API keys typically start with 'AIza' and are 39 characters long
    return api_key.startswith('AIza') and len(api_key) == 39

# ---------------- PDF Functions ----------------
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    return splitter.split_text(text)

def get_vector_store(chunks):
    # Use cached embeddings if available
    if 'embeddings' not in st.session_state:
        st.session_state.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    embeddings = st.session_state.embeddings
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

def get_conversational_chain(api_key):
    prompt_template = """
💬 Hi there! Please help answer the user's question as clearly and thoroughly as possible using only the information in the context below.  
📌 If the answer is not in the context, just say "🙁 I'm afraid I don't have that info in the provided context."  
❌ Do not guess or make up answers.  

📄 Context:
{context}

❓ Question:
{question}

💡 Answer:
Please explain in a friendly and easy-to-understand way. You can also add tips or examples if it helps the user understand better. Thank you! 🙏
"""

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3, google_api_key=api_key)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain


def user_input(user_question, pdf_docs, conversation_history, api_key):
    # ---------------- Check for special keywords first ----------------
    should_handle, special_response = handle_special_keywords(user_question, conversation_history)
    if should_handle:
        conversation_history.append((user_question, special_response, "Assistant", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ""))
        # Save to persistent history file
        add_chat(
            user_question, special_response, "Assistant",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ", ".join([pdf.name for pdf in pdf_docs]) if pdf_docs else ""
        )
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_question)
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(special_response)
        # Always show download button for any special response
        if len(conversation_history) > 0:
            text_history = ""
            for q, a, model, ts, pdf in conversation_history:
                text_history += f"Question: {q}\nAnswer: {a}\nModel: {model}\nTimestamp: {ts}\nPDFs: {pdf}\n{'-'*50}\n"
            b64 = base64.b64encode(text_history.encode()).decode()
            st.sidebar.markdown(f'<a href="data:file/txt;base64,{b64}" download="conversation_history.txt">'
                                f'<button style="background-color:#888; color:#fff; border:none; padding:8px 16px; border-radius:5px; cursor:pointer; font-size:16px;">Download conversation history</button></a>', unsafe_allow_html=True)
        return

    # ---------------- Check API key ----------------
    if not validate_api_key(api_key):
        st.error("❌ Invalid or missing Google API key. Please enter a valid API key in the sidebar.")
        return

    # ---------------- PDF handling with caching ----------------
    if not pdf_docs:
        st.warning("⚠️ Please upload PDF files.")
        return

    try:
        # Create a unique key for uploaded PDFs based on their names and sizes
        pdf_key = tuple((pdf.name, pdf.size) for pdf in pdf_docs)

        # If PDFs changed, re-process and cache
        if ('pdf_key' not in st.session_state or st.session_state.pdf_key != pdf_key):
            text = get_pdf_text(pdf_docs)
            text_chunks = get_text_chunks(text)
            vector_store = get_vector_store(text_chunks)
            st.session_state.pdf_key = pdf_key
            st.session_state.text_chunks = text_chunks
            st.session_state.vector_store = vector_store
        else:
            text_chunks = st.session_state.text_chunks
            vector_store = st.session_state.vector_store

        # Load vector DB from cache
        embeddings = st.session_state.embeddings
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

        # Similarity search
        docs = new_db.similarity_search(user_question)

        # Gemini LLM
        chain = get_conversational_chain(api_key)
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

        user_question_output = user_question
        response_output = response['output_text']
        pdf_names = [pdf.name for pdf in pdf_docs] if pdf_docs else []

        # Save history (session)
        conversation_history.append((user_question_output, response_output, "Google AI", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ", ".join(pdf_names)))
        # Save to persistent history file
        add_chat(
            user_question_output, response_output, "Google AI",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ", ".join(pdf_names)
        )

        # Display chat messages
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_question_output)
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response_output)

        # Download history as text file
        if len(conversation_history) > 0:
            text_history = ""
            for q, a, model, ts, pdf in conversation_history:
                text_history += f"Question: {q}\nAnswer: {a}\nModel: {model}\nTimestamp: {ts}\nPDFs: {pdf}\n{'-'*50}\n"

            b64 = base64.b64encode(text_history.encode()).decode()
            st.sidebar.markdown(f'<a href="data:file/txt;base64,{b64}" download="conversation_history.txt">'
                                f'<button style="background-color:#888; color:#fff; border:none; padding:8px 16px; border-radius:5px; cursor:pointer; font-size:16px;">Download conversation history</button></a>', unsafe_allow_html=True)

    except Exception as e:
        if "API_KEY" in str(e).upper() or "AUTHENTICATION" in str(e).upper():
            st.error("❌ API key authentication failed. Please check your Google API key.")
        else:
            st.error(f"❌ An error occurred: {str(e)}")


# ---------------- Run Chatbot Page ----------------
def run_chatbot():
    st.header("📚 Chat with multiple PDFs")

    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'user_api_key' not in st.session_state:
        st.session_state.user_api_key = ''

    # ---------------- Sidebar for API Key and File Upload ----------------
    st.sidebar.markdown('<h3 style="font-size:23px; font-weight:600; margin-bottom:0;">🔧 Configuration</h3>', unsafe_allow_html=True)
    # API Key Section
    st.sidebar.markdown('<h3 style="font-size:20px; font-weight:600; margin-bottom:0;">🔑 Google API Key</h3>', unsafe_allow_html=True)
    
    # Check if config API key exists and is valid
    config_api_key = ""
    try:
        config_api_key = config.GOOGLE_API_KEY
        if not validate_api_key(config_api_key):
            config_api_key = ""
    except (AttributeError, ImportError):
        pass
    
    # User input for API key
    user_api_key = st.sidebar.text_input(
        "Enter Google API Key:",
        value=st.session_state.user_api_key,
        type="password",
        help="Enter your Google Gemini API key if the key is not working"
    )

    # Update session state
    if user_api_key != st.session_state.user_api_key:
        st.session_state.user_api_key = user_api_key

    # Only show warning or success after user input
    current_api_key = config_api_key if config_api_key else st.session_state.user_api_key
    api_key = config_api_key if config_api_key else user_api_key

    if validate_api_key(api_key):
        st.sidebar.success("✅ API key is valid and ready")
    else:
        st.sidebar.warning("⚠️ API key is invalid.\nPlease enter your API key below.")
        st.sidebar.info("💡 Get your API key from: https://aistudio.google.com/apikey")
        
        
    st.sidebar.markdown("---")

    # File Upload Section
    st.sidebar.markdown('<h3 style="font-size:20px; font-weight:600; margin-bottom:0;">📁 Upload Files</h3>', unsafe_allow_html=True)
    pdf_docs = st.sidebar.file_uploader("Upload your PDFs", accept_multiple_files=True)
    st.sidebar.markdown("---")

    # Clear Chat Button
    if st.sidebar.button("🧹 Clear Chat History"):
        st.session_state.conversation_history = []
        st.rerun()

    if st.sidebar.button("Process PDFs"):
        if not validate_api_key(api_key):
            st.sidebar.error("❌ Please enter a valid API key first")
        elif pdf_docs:
            with st.spinner("Processing PDFs..."):
                try:
                    chunks = get_text_chunks(get_pdf_text(pdf_docs))
                    get_vector_store(chunks)
                    st.sidebar.success("✅ PDFs processed successfully!")
                except Exception as e:
                    st.sidebar.error(f"❌ Error processing PDFs: {str(e)}")
        else:
            st.sidebar.warning("Please upload PDF files first.")


    # ---------------- Main Chat Interface ----------------
    # Show previous chats
    st.subheader("💬 Conversation")
    for q, a, model, ts, pdf in st.session_state.conversation_history:
        with st.chat_message("user", avatar="🧑"):
            st.markdown(q)
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(a)
            with st.expander("Details"):
                
                st.write(f"📄 PDFs: {pdf}")
                st.write(f"⏰ {ts}")

    # Chat input
    user_question = st.chat_input("Ask a question about your PDFs...")
    if user_question:
        user_input(user_question, pdf_docs, st.session_state.conversation_history, api_key)
