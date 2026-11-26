import streamlit as st
from llm_chains import load_normal_chain, load_pdf_chat_chain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from streamlit_mic_recorder import mic_recorder
from utils import save_chat_history_json, get_timestamp, load_chat_history_json
from audio_handler import transcribe_audio
from image_handler import answer_image_question
from pdf_handler import add_documents_to_db
from html_templates import (
    get_bot_template,
    get_user_template,
    get_welcome_template,
    css,
)
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

with CONFIG_PATH.open("r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

CHAT_HISTORY_PATH = PROJECT_ROOT / str(config["chat_history_path"]).lstrip("./\\")
CHAT_HISTORY_PATH.mkdir(parents=True, exist_ok=True)

def load_chain(chat_history):
    if st.session_state.pdf_chat:
        print("loading pdf chat chain")
        return load_pdf_chat_chain(chat_history)
    return load_normal_chain(chat_history)

def clear_input_field():
    if st.session_state.user_question == "":
        st.session_state.user_question = st.session_state.user_input
        st.session_state.user_input = ""

def set_send_input():
    st.session_state.send_input = True
    clear_input_field()

def toggle_pdf_chat():
    st.session_state.pdf_chat = True

def save_chat_history():
    if st.session_state.history:
        if st.session_state.session_key == "new_session":
            st.session_state.new_session_key = get_timestamp() + ".json"
            save_chat_history_json(st.session_state.history, CHAT_HISTORY_PATH / st.session_state.new_session_key)
        else:
            save_chat_history_json(st.session_state.history, CHAT_HISTORY_PATH / st.session_state.session_key)

def main():
    st.write(css, unsafe_allow_html=True)
    
    st.sidebar.title("Chat Sessions")
    chat_sessions = ["new_session"] + sorted(
        path.name for path in CHAT_HISTORY_PATH.glob("*.json") if path.is_file()
    )

    if "send_input" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.send_input = False
        st.session_state.user_question = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"
    if st.session_state.session_key == "new_session" and st.session_state.new_session_key is not None:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None

    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key", index=index)
    st.sidebar.toggle("PDF Chat", key="pdf_chat", value=False)

    if st.session_state.session_key != "new_session":
        st.session_state.history = load_chat_history_json(CHAT_HISTORY_PATH / st.session_state.session_key)
    else:
        st.session_state.history = []

    chat_history = StreamlitChatMessageHistory(key="history")
    
    chat_container = st.container()
    if not chat_history.messages:
        st.markdown(get_welcome_template(), unsafe_allow_html=True)

    with st.container(key="composer"):
        message_column, voice_column, send_column = st.columns([6, 1.5, 1.5])
        with message_column:
            st.text_input(
                "Message",
                key="user_input",
                placeholder="Ask BharatGPT anything...",
                label_visibility="collapsed",
                on_change=set_send_input,
            )
        with voice_column:
            voice_recording = mic_recorder(
                start_prompt="🎙️ Voice",
                stop_prompt="⏹️ Stop",
                just_once=True,
            )
        with send_column:
            send_button = st.button(
                "Send",
                key="send_button",
                on_click=clear_input_field,
                use_container_width=True,
            )

    uploaded_audio = st.sidebar.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])
    uploaded_pdf = st.sidebar.file_uploader("Upload a pdf file", accept_multiple_files=True, key="pdf_upload", type=["pdf"], on_change=toggle_pdf_chat)
    if st.sidebar.button("Clear image"):
        st.session_state.pop("image_upload", None)
    uploaded_image = st.sidebar.file_uploader(
        "Upload an image",
        key="image_upload",
        type=["jpg", "jpeg", "png", "webp"],
    )
    if uploaded_image:
        st.sidebar.image(uploaded_image, caption=uploaded_image.name)

    if uploaded_pdf:
        with st.spinner("Processing PDF..."):
            add_documents_to_db(uploaded_pdf)
    
    transcribe_audio_button = st.sidebar.button(
        "Transcribe audio",
        disabled=uploaded_audio is None,
    )
    if uploaded_audio and transcribe_audio_button:
        try:
            transcribed_audio = transcribe_audio(uploaded_audio.getvalue())
            st.caption("Transcript: " + transcribed_audio)
            llm_chain = load_chain(chat_history)
            llm_response = llm_chain.run(
                "Summarize this transcript:\n" + transcribed_audio
            )
            st.write(llm_response)
        except Exception as error:
            st.error(f"Could not process the uploaded audio: {error}")

    if voice_recording:
        try:
            transcribed_audio = transcribe_audio(voice_recording["bytes"])
            st.caption("Transcript: " + transcribed_audio)
            llm_chain = load_chain(chat_history)
            llm_response = llm_chain.run(transcribed_audio)
            st.write(llm_response)
        except Exception as error:
            st.error(f"Could not process the recording: {error}")

    if send_button or st.session_state.send_input:
        if st.session_state.user_question.strip() or uploaded_image:
            try:
                user_question = st.session_state.user_question.strip()
                if uploaded_image:
                    image_question = user_question or "Describe this image."
                    llm_response = answer_image_question(
                        uploaded_image.getvalue(),
                        uploaded_image.type,
                        image_question,
                    )
                    chat_history.add_user_message(
                        f"{image_question}\n[Image: {uploaded_image.name}]"
                    )
                    chat_history.add_ai_message(llm_response)
                else:
                    llm_chain = load_chain(chat_history)
                    llm_response = llm_chain.run(user_question)
                if not llm_response or llm_response.strip() == "":
                    llm_response = "[WARNING] No relevant information found. Try asking differently!"
                st.write(llm_response)
            except Exception as error:
                st.error(f"Could not generate a response: {error}")
            finally:
                st.session_state.user_question = ""

        st.session_state.send_input = False

    if chat_history.messages != []:
        with chat_container:
            st.write("Chat History:")
            for message in reversed(chat_history.messages):
                if message.type == "human":
                    st.write(get_user_template(message.content), unsafe_allow_html=True)
                else:
                    st.write(get_bot_template(message.content), unsafe_allow_html=True)

    save_chat_history()

if __name__ == "__main__":
    main()
