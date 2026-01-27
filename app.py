import streamlit as st
import google.generativeai as genai
from PIL import Image
import uuid
import re
import os                       # <--- Add this
from dotenv import load_dotenv  # <--- Add this

# 1. Configuration & API Setup (The Secure Way)
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# --- SYSTEM PERSONA ---
SYSTEM_PROMPT = """
You are 'CaptionBot Pro'. 
Provide the requested number of captions. 
CRITICAL: Separate each caption with the exact string '---SPLIT---'. 
Do not include any other text, labels, or intros. Just the clean captions.
"""

# 2. Page Config & Custom Branding CSS
st.set_page_config(page_title="CaptionBot SaaS", layout="wide", page_icon="🤖")

st.markdown("""
    <style>
    /* Custom Header Styling */
    .main-header {
        font-size: 36px;
        font-weight: 700;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 0px;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .sub-header {
        font-size: 16px;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    /* Sidebar branding */
    .sidebar-brand {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        background: #2a3140;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE MULTI-CHAT STATE ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}
if "current_chat_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.current_chat_id = new_id
    st.session_state.all_chats[new_id] = {"messages": [], "image": None}

# --- FUNCTIONS ---
def delete_chat(chat_id_to_del):
    del st.session_state.all_chats[chat_id_to_del]
    if st.session_state.current_chat_id == chat_id_to_del:
        if st.session_state.all_chats:
            st.session_state.current_chat_id = list(st.session_state.all_chats.keys())[0]
        else:
            new_id = str(uuid.uuid4())
            st.session_state.all_chats[new_id] = {"messages": [], "image": None}
            st.session_state.current_chat_id = new_id

# --- SIDEBAR: BRANDING & HISTORY ---
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🤖 CaptionBot Pro</div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state.all_chats[new_id] = {"messages": [], "image": None}
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.divider()
    st.subheader("Recent History")
    
    for chat_id in reversed(list(st.session_state.all_chats.keys())):
        chat_data = st.session_state.all_chats[chat_id]
        label = chat_data["messages"][0]["content"][:18] + ".." if chat_data["messages"] else "New Empty Chat"
        
        col_select, col_del = st.columns([0.8, 0.2])
        with col_select:
            is_active = chat_id == st.session_state.current_chat_id
            if st.button(label, key=f"s_{chat_id}", use_container_width=True, disabled=is_active):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"d_{chat_id}"):
                delete_chat(chat_id)
                st.rerun()

# --- MAIN INTERFACE ---
st.markdown('<div class="main-header">CaptionBot SaaS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">The ultimate AI engine for social media captions</div>', unsafe_allow_html=True)

current_chat = st.session_state.all_chats[st.session_state.current_chat_id]

# Display History
for msg in current_chat["messages"]:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            caps = msg["content"].split("---SPLIT---")
            for c in caps:
                if c.strip(): st.code(c.strip(), language=None)
        else:
            st.markdown(msg["content"])

# --- INPUT & AI LOGIC ---
prompt_data = st.chat_input("Ex: 'Give me 4 captions for this'", accept_file=True)

if prompt_data:
    user_text = prompt_data.text
    user_image = None
    if prompt_data.files:
        user_image = Image.open(prompt_data.files[0])
        current_chat["image"] = user_image
    
    # Logic to find number of captions
    requested_count = 3
    if user_text:
        numbers = re.findall(r'\d+', user_text)
        if numbers: requested_count = int(numbers[0])

    with st.chat_message("user"):
        if user_text: st.markdown(user_text)
        if user_image: st.image(user_image, width=300)

    current_chat["messages"].append({"role": "user", "content": user_text if user_text else f"Generate {requested_count} captions"})

    try:
        model = genai.GenerativeModel('gemini-flash-latest', system_instruction=SYSTEM_PROMPT)
        content_payload = [f"User wants {requested_count} captions. Detail: {user_text}"]
        
        img_to_use = user_image if user_image else current_chat["image"]
        if img_to_use: content_payload.append(img_to_use)
            
        with st.chat_message("assistant"):
            with st.spinner("Writing..."):
                response = model.generate_content(content_payload)
                caps = response.text.split("---SPLIT---")
                for c in caps:
                    if c.strip(): st.code(c.strip(), language=None)
        
        current_chat["messages"].append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Error: {e}")