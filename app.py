import os
import re
import uuid
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. Configuration & API Setup
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

CANDIDATE_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
]

# --- SYSTEM PERSONA ---
SYSTEM_PROMPT = """
You are 'CaptionBot Pro'.
Provide the requested number of captions.
CRITICAL: Separate each caption with the exact string '---SPLIT---'.
Do not include any other text, labels, or intros. Just the clean captions.
"""

# 2. Page Config & Original Branding CSS
st.set_page_config(page_title="CaptionBot", layout="wide", page_icon="🤖")

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


def generate_captions(prompt_text: str, image=None, count: int = 3) -> str:
    if not API_KEY:
        raise ValueError("API key missing. Set GOOGLE_API_KEY or GEMINI_API_KEY in your .env file.")

    client = genai.Client(
        api_key=API_KEY,
        http_options=types.HttpOptions(timeout=15_000),
    )

    content_payload = [f"User wants {count} captions. Detail: {prompt_text}"]
    if image is not None:
        content_payload.append(image)

    last_err = None
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=content_payload,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )
            if response.text:
                return response.text
        except APIError as e:
            last_err = e
            if e.code in (404, 429, 503):
                continue
            raise

    raise RuntimeError(f"Could not generate captions right now. Last error: {last_err}")


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
st.markdown('<div class="main-header">CaptionBot by Dev Faruk</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">The ultimate AI engine for social media captions</div>', unsafe_allow_html=True)

current_chat = st.session_state.all_chats[st.session_state.current_chat_id]

# Display History
for msg in current_chat["messages"]:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            caps = msg["content"].split("---SPLIT---")
            for c in caps:
                if c.strip():
                    st.code(c.strip(), language=None)
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
        numbers = re.findall(r"\d+", user_text)
        if numbers:
            requested_count = int(numbers[0])

    with st.chat_message("user"):
        if user_text:
            st.markdown(user_text)
        if user_image:
            st.image(user_image, width=300)

    current_chat["messages"].append({
        "role": "user",
        "content": user_text if user_text else f"Generate {requested_count} captions",
    })

    try:
        img_to_use = user_image if user_image else current_chat["image"]
        with st.chat_message("assistant"):
            with st.spinner("Writing..."):
                result_text = generate_captions(
                    prompt_text=user_text or "",
                    image=img_to_use,
                    count=requested_count,
                )
                caps = result_text.split("---SPLIT---")
                for c in caps:
                    if c.strip():
                        st.code(c.strip(), language=None)

        current_chat["messages"].append({"role": "assistant", "content": result_text})
    except Exception as e:
        st.error(f"Error: {e}")