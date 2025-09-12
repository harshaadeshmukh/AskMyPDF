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
    

    # ---------------- Greetings ----------------
    hello_keywords = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", "hola", "namaste"]
    hello_responses = [
        "👋 Hello there! Ready to dive into some PDF magic? What would you like to explore today?",
        "🌟 Hey! I'm your PDF companion - let's unlock some knowledge together!",
        "👋 Greetings! I'm here to make your PDFs talk. What secrets shall we uncover?",
        "🤖 Hello human! Time to turn your documents into conversations. What's on your mind?",
        "✨ Hi! Consider me your personal PDF whisperer. What would you like to know?"
    ]
    
    # ---------------- Current Date/Time ----------------
    date_keywords = ["date", "today", "what day", "current date", "todays date", "what's the date"]
    time_keywords = ["time", "current time", "what time", "clock"]
    
    # ---------------- How was your day ----------------
    day_keywords = ["how was your day", "how is your day", "how are you doing", "how is it going", "what's up" , "whats up" , "how are you"]
    day_responses = [
        "🤖 My day's been fantastic! I've been helping people chat with their PDFs and it's absolutely electrifying! ⚡ How about you?",
        "📚 Amazing! I spent my day diving deep into documents and surfacing insights. It's like being a digital archaeologist! How's your day going?",
        "💫 Wonderful! I've been busy turning static text into dynamic conversations. Each PDF is like a new adventure! What about your day?",
        "🎯 Brilliant! I love connecting people with their document's hidden knowledge. It's like matchmaking, but for information! How are you?",
        "🚀 Incredible! Every question you humans ask teaches me something new about curiosity. Speaking of which, how's your day treating you?"
    ]
        
    # ---------------- Who are you / About ----------------
    about_keywords = ["who are you", "what are you", "about you", "introduce yourself", "tell me about yourself"]
    about_responses = [
        "🤖 I'm your friendly PDF assistant! Think of me as a librarian who never sleeps and loves turning documents into conversations. What can I help you discover?",
        "📚 I'm a digital document whisperer! I speak fluent PDF and love helping people unlock the knowledge hidden in their files. Ready to explore?",
        "✨ I'm your AI-powered reading companion! I transform boring document searches into exciting knowledge quests. What adventure shall we embark on?",
        "🎯 I'm a knowledge extraction specialist! I turn your PDFs into chatty companions. Think of me as your personal document translator!"
    ]
    
    # ---------------- Capabilities ----------------
    capability_keywords = ["what can you do", "help", "capabilities", "features", "how do you work"]
    capability_responses = [
        "🚀 I can:\n• 📄 Read and understand your PDFs\n• 🔍 Search through multiple documents instantly\n• 💬 Answer questions in plain English\n• 📝 Summarize content\n• 🎯 Find specific information\n• 💡 Provide insights and explanations\n\nJust upload your PDFs and start asking!",
        "⚡ My superpowers include:\n• 📚 Speed-reading entire documents in seconds\n• 🧠 Understanding context and meaning\n• 🔗 Connecting information across multiple PDFs\n• 💭 Explaining complex topics simply\n• 🎪 Making boring documents entertaining!\n\nWhat would you like to explore?",
        "🌟 I'm your PDF Swiss Army knife! I can:\n• 📖 Extract key information\n• 🔍 Perform semantic search\n• 💬 Engage in document-based conversations\n• 📊 Analyze and compare content\n• 🎓 Help with research and study\n\nLet's get started!"
    ]
    
    # ...existing code...

    # ---------------- Jokes/Fun ----------------
    joke_keywords = ["joke", "funny", "laugh", "humor", "entertain me"]
    joke_responses = [
        "😄 Why don't PDFs ever get lost? Because they always have their bookmarks! 📖✨",
        "🤣 What's a PDF's favorite type of music? Heavy Meta-data! 🎵📄",
        "😂 Why did the PDF go to therapy? It had too many layers and needed to decompress! 🗂️💆‍♀️",
        "🎭 What do you call a PDF that tells jokes? A Comic Sans document! (Sorry, that was terrible! 😅)",
        "😆 Why are PDFs great at parties? They always bring the right format! 🎉📋"
    ]
    
    # ---------------- Goodbye ----------------
    goodbye_keywords = ["bye", "goodbye", "see you", "farewell", "exit", "quit"]
    goodbye_responses = [
        "👋 Goodbye! Remember, your PDFs and I will be here whenever you need us. Happy reading! 📚✨",
        "🌟 See you later! May your documents be ever searchable and your answers always found! 🔍💫",
        "👋 Farewell, knowledge seeker! Come back anytime you need to chat with your PDFs! 📄💬",
        "✨ Until next time! Keep exploring, keep questioning, and keep learning! 🚀📖"
    ]
    
    # ---------------- Compliments ----------------
    compliment_keywords = ["good job", "great", "awesome", "excellent", "amazing", "wonderful", "fantastic", "brilliant"]
    compliment_responses = [
        "🥰 Aww, thank you! You're pretty awesome yourself for exploring knowledge through your documents! ⭐",
        "😊 That means a lot! I'm just happy to help you unlock the treasures in your PDFs! 💎📚",
        "🌟 You're too kind! Team work makes the dream work - you ask great questions! 🤝✨",
        "💖 Thanks! I love helping curious minds like yours dive deep into documents! 🤿📄",
        "🎉 You're making my circuits happy! Keep those questions coming! ⚡🤖"
    ]
    
    # ---------------- Check keyword matches and respond ----------------
    
    if any(keyword in user_question_lower for keyword in hello_keywords):
        return True, random.choice(hello_responses)
    
    elif any(keyword in user_question_lower for keyword in date_keywords):
        current_date = datetime.now()
        formatted_date = current_date.strftime("%B %d, %Y")
        day_name = current_date.strftime("%A")
        responses = [
            f"📅 Today is {day_name}, {formatted_date}! Perfect day for some PDF exploration, don't you think? ✨",
            f"🗓️ It's {formatted_date} ({day_name}) - time flies when you're having fun with documents! ⏰📚",
            f"📆 Today's date is {formatted_date}! A {day_name} well spent reading PDFs is a day well spent indeed! 🌟"
        ]
        return True, random.choice(responses)
    
    elif any(keyword in user_question_lower for keyword in time_keywords):
        current_time = datetime.now().strftime("%I:%M %p")
        responses = [
            f"🕐 It's {current_time} - always a good time to learn something new from your PDFs! ⏰✨",
            f"⏰ The time is {current_time}. Time for some document adventures? 🚀📄",
            f"🕒 Current time: {current_time} - every moment is a great moment for knowledge discovery! 💡"
        ]
        return True, random.choice(responses)
    
    elif any(keyword in user_question_lower for keyword in day_keywords):
        return True, random.choice(day_responses)
      
    elif any(keyword in user_question_lower for keyword in about_keywords):
        return True, random.choice(about_responses)
    
    elif any(keyword in user_question_lower for keyword in capability_keywords):
        return True, random.choice(capability_responses)
    
    elif any(keyword in user_question_lower for keyword in joke_keywords):
        return True, random.choice(joke_responses)
    
    elif any(keyword in user_question_lower for keyword in goodbye_keywords):
        return True, random.choice(goodbye_responses)
    
    elif any(keyword in user_question_lower for keyword in compliment_keywords):
        return True, random.choice(compliment_responses)
    
    # ---------------- Special Creative Responses ----------------
    elif "age" in user_question_lower or "old are you" in user_question_lower:
        return True, "🤖 I'm as old as your latest PDF upload and as young as your next question! Age is just a number in the digital realm! ✨🔢"
    
    elif "birthday" in user_question_lower:
        return True, "🎂 I celebrate my birthday every time you upload a new PDF! Each document gives me new life and purpose! 🎉📚"
    
    elif "favorite" in user_question_lower:
        favorites = [
            "📚 My favorite thing? Discovering hidden gems in your documents!",
            "🔍 I love connecting dots between different parts of your PDFs!",
            "💡 My favorite moments are when I help you find exactly what you need!",
            "✨ I'm passionate about turning complex documents into simple conversations!"
        ]
        return True, random.choice(favorites)
    

    # Special gratitude responses (enhanced from original)
    elif any(keyword in user_question_lower for keyword in ["thank you", "thanks", "dhanyavaad", "thank you so much", "great job"]):
        gratitude_responses = [
            "🤗 My pleasure! That's what I'm here for - making your PDF journey smoother!",
            "😊 You're very welcome! Happy to help a fellow knowledge explorer!",
            "✨ Anytime! Your curiosity makes my circuits happy!",
            "🌟 Glad I could help! Keep those questions coming!",
            "💫 You're so welcome! Together we're unlocking document mysteries!"
        ]
        return True, random.choice(gratitude_responses)
    
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
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
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
        # Save to history
        conversation_history.append((user_question, special_response, "Assistant", 
                                   datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ""))
        
        # Display chat messages
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_question)
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(special_response)
        return

    # ---------------- Check API key ----------------
    if not validate_api_key(api_key):
        st.error("❌ Invalid or missing Google API key. Please enter a valid API key in the sidebar.")
        return

    # ---------------- Original PDF handling code ----------------
    if not pdf_docs:
        st.warning("⚠️ Please upload PDF files.")
        return

    try:
        # Process PDFs
        text_chunks = get_text_chunks(get_pdf_text(pdf_docs))
        get_vector_store(text_chunks)

        # Load vector DB
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

        # Similarity search
        docs = new_db.similarity_search(user_question)

        # Gemini LLM
        chain = get_conversational_chain(api_key)
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

        user_question_output = user_question
        response_output = response['output_text']
        pdf_names = [pdf.name for pdf in pdf_docs] if pdf_docs else []

        # Save history
        conversation_history.append((user_question_output, response_output, "Google AI",
                                     datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ", ".join(pdf_names)))

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
                                f'<button>Download conversation history</button></a>', unsafe_allow_html=True)

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
    st.sidebar.header("🔧 Configuration")
    
    # API Key Section
    st.sidebar.subheader("🔑 Google API Key")
    
    # Check if config API key exists and is valid
    config_api_key = ""
    try:
        config_api_key = config.GOOGLE_API_KEY
        if validate_api_key(config_api_key):
            st.sidebar.success("✅ API key is valid")
        else:
            config_api_key = ""
    except (AttributeError, ImportError):
        pass
    
    # Only show warning if no valid API key is available
    current_api_key = config_api_key if config_api_key else st.session_state.user_api_key
    
    if not validate_api_key(current_api_key):
        st.sidebar.warning("⚠️ API key is invalid.\nPlease enter your API key below.")
    
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
    
    # Determine which API key to use
    api_key = config_api_key if config_api_key else user_api_key
    
    # API Key status
    if validate_api_key(api_key):
        st.sidebar.success("✅ API key is ready")
    else:
        st.sidebar.error("❌ Please enter a valid Google API key")
        st.sidebar.info("💡 Get your API key from: https://console.cloud.google.com/")
        

    # File Upload Section
    st.sidebar.subheader("📁 Upload Files")
    pdf_docs = st.sidebar.file_uploader("Upload your PDFs", accept_multiple_files=True)

    if st.sidebar.button("Process PDFs"):
        if not validate_api_key(api_key):
            st.sidebar.error("❌ Please enter a valid API key first")
        elif pdf_docs:
            with st.spinner("Processing PDFs..."):
                try:
                    chunks = get_text_chunks(get_pdf_text(pdf_docs))
                    get_vector_store(chunks)
                    st.success("✅ PDFs processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error processing PDFs: {str(e)}")
        else:
            st.warning("Please upload PDF files first.")


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
                st.write(f"⚡ Model: {model}")

    # Chat input
    user_question = st.chat_input("Ask a question about your PDFs...")
    if user_question:
        user_input(user_question, pdf_docs, st.session_state.conversation_history, api_key)