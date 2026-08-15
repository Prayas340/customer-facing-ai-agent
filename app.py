import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Load environment variables from .env if present
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Customer Facing AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        max-width: 1000px;
        margin: 0 auto;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: #e8f0fe;
        color: #1a73e8;
        margin-bottom: 10px;
    }
    .system-card {
        padding: 14px 18px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border-left: 4px solid #1a73e8;
        margin-bottom: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# --- System Persona & Instructions ---
SYSTEM_INSTRUCTION = """
You are 'Apex Assistant', a friendly, professional, and knowledgeable Customer Experience and Support representative for Apex Retail.
Your goal is to provide fast, courteous, and highly accurate assistance to customers.

Key Guidelines:
1. Tone & Persona: Warm, professional, empathetic, and solution-oriented.
2. Domain Expertise:
   - Order Status & Tracking: Inquire politely about Order IDs (e.g., #ORD-12345) and provide structured, helpful tracking responses.
   - Return & Refund Policy: Apex offers a 30-day hassle-free return policy for unused items in original packaging. Refunds are processed within 3-5 business days.
   - Shipping: Standard shipping (3-5 business days), Express shipping (1-2 business days), and Free shipping on orders over $50.
   - Warranty & Support: 1-year limited warranty on electronics and hardware.
3. Multi-turn context: Remember customer details, questions, and previous context throughout the ongoing conversation.
4. Formatting: Use clear formatting, bullet points, and bold text to make instructions easy to read.
5. Boundaries: If a query cannot be resolved directly, offer to escalate the ticket to a human specialist with support email support@apexretail.example.com.
"""

# Available models in priority order for seamless fallback
MODELS_PRIORITY = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest"
]
DEFAULT_MODEL = MODELS_PRIORITY[0]

# --- Resolve API Key ---
def get_api_key() -> str | None:
    # 1. Environment variable (Cloud Run or .env)
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ.get("GEMINI_API_KEY")
    # 2. Streamlit secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    # 3. Session state (if user entered via sidebar)
    if "user_api_key" in st.session_state and st.session_state.user_api_key:
        return st.session_state.user_api_key
    return None


api_key = get_api_key()

# --- Sidebar UI ---
with st.sidebar:
    st.title("🤖 Apex Retail Support")
    st.caption("Customer Facing AI Agent")
    st.markdown("---")
    st.markdown("### 💡 Quick Inquiries")
    sample_queries = [
        "📦 Where is my order #ORD-98421?",
        "🔄 What is your 30-day return policy?",
        "🚚 How much does express shipping cost?",
        "🛠️ How do I file a warranty claim?"
    ]
    for sq in sample_queries:
        if st.button(sq, use_container_width=True):
            st.session_state.pending_prompt = sq

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        st.rerun()

# --- Header & Welcome Banner ---
st.title("Customer Facing AI Agent")
st.markdown("Welcome to **Apex Customer Support**. How can we help you today with your orders, returns, or product questions?")

# --- API Key Validation Guard ---
if not api_key:
    st.info(
        """
        ### 🔑 Action Required: Provide Gemini API Key
        To interact with the customer-facing agent:
        1. Set the **`GEMINI_API_KEY`** environment variable in `.env` or Google Cloud Run.
        2. Or enter your key in the sidebar on the left.
        
        *Get your free API key at [Google AI Studio](https://aistudio.google.com/).*
        """
    )
    st.stop()

# --- Helper to initialize Chat session ---
def init_chat(client: genai.Client, model_name: str):
    return client.chats.create(
        model=model_name,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,
            top_p=0.95,
        )
    )

# --- Initialize Gemini Client and Multi-turn Chat Session ---
if "client" not in st.session_state or st.session_state.get("client_api_key") != api_key:
    st.session_state.client = genai.Client(api_key=api_key)
    st.session_state.client_api_key = api_key
    st.session_state.active_model = DEFAULT_MODEL
    if "chat" in st.session_state:
        del st.session_state.chat

if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! 👋 Welcome to Apex Retail Support. I'm Apex Assistant. How can I help you today with your orders, shipments, returns, or product inquiries?"
        }
    ]

if "chat" not in st.session_state:
    st.session_state.chat = init_chat(st.session_state.client, DEFAULT_MODEL)

# --- Display Chat History ---
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Handle User Input ---
prompt = None
if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
else:
    prompt = st.chat_input("Type your question or message here...")

if prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate assistant streaming response
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        full_response = ""
        
        success = False
        last_error = None
        
        for try_model in MODELS_PRIORITY:
            try:
                with st.spinner("Apex Assistant is thinking..."):
                    if st.session_state.get("active_model") != try_model:
                        st.session_state.chat = init_chat(st.session_state.client, try_model)
                        st.session_state.active_model = try_model
                    
                    response_stream = st.session_state.chat.send_message_stream(prompt)
                    full_response = ""
                    for chunk in response_stream:
                        if chunk.text:
                            full_response += chunk.text
                            response_container.markdown(full_response + "▌")
                    
                    response_container.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    success = True
                    break
            except (APIError, Exception) as e:
                last_error = e
                # Fall back to next model in priority list
                continue
        
        if not success:
            err_text = str(last_error)
            error_msg = f"⚠️ **Error connecting to Gemini:** {err_text}"
            response_container.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
