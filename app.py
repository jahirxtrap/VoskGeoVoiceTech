import streamlit as st
import pickle
import os
import threading
import queue
from engine.vosk_recog import speech_to_text

# Configuración de la página
st.set_page_config(layout="wide", page_icon="./media/logo.png", page_title="Geo-Voice Tech")

# Función de hilo para el reconocimiento de voz
def voice_recognition_thread(q, model_path="./model/vosk-model-small-es-0.42"):
    q.put("Empiece a hablar...")
    try:
        for speech in speech_to_text(prints=False, model_path=model_path, device_index=1):
            q.put(speech)
            if "stop" in speech or "parate" in speech:  # Detectar "parate" para detener
                q.put("stop")
                break
    except Exception as e:
        q.put(f"Error: {str(e)}")
        q.put("stop")

# Cargar o crear directorio de datos
data_dir = "./data/"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Inicialización de sesiones/variables
def initialize_session_state():
    try:
        with open(os.path.join(data_dir, "pages"), "rb") as file:
            session_state_data = pickle.load(file)
            if "page_history" in session_state_data:
                st.session_state.page_history = session_state_data["page_history"]
            if "page_number" in session_state_data:
                st.session_state.page_number = session_state_data["page_number"]
    except FileNotFoundError:
        if "page_history" not in st.session_state:
            st.session_state.page_history = []
        if "page_number" not in st.session_state:
            st.session_state.page_number = 1
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

initialize_session_state()

def save_session_state():
    session_state_data = {
        "page_history": st.session_state.page_history,
        "page_number": st.session_state.page_number
    }
    with open("./data/pages", "wb") as file:
        pickle.dump(session_state_data, file)

# Función para mostrar mensajes
def show_messages():
    for n, sender, message in st.session_state.page_history:
        if n == st.session_state.current_page:
            if sender == "user":
                st.chat_message(sender).write(message)

# Función para enviar mensaje
def message(page, prompt):
    st.session_state.page_history.append((page, "user", prompt))
    show_messages()
    save_session_state()
    st.rerun()

# Barra lateral
with st.sidebar:
    st.image("./media/banner.png", use_column_width=True)
    st.header("Diario")

    # Botón nueva página
    if st.button("Nueva página", use_container_width=True):
        st.session_state.page_number += 1
        st.session_state.current_page = st.session_state.page_number
        save_session_state()

    # Historial de páginas
    st.header("Historial")
    for n in range(st.session_state.page_number):
        page_title = "Página {}".format(n + 1)
        if st.button(page_title, use_container_width=True):
            st.session_state.current_page = n + 1
    st.divider()

    # Botón eliminar historial
    if st.button("Eliminar Historial", use_container_width=True):
        if os.path.exists("./data/pages"):
            st.session_state.page_history = []
            st.session_state.page_number = 1
            os.remove("./data/pages")
            st.rerun()

# Entrada del usuario
col1, col2 = st.columns([7, 1])
col1.header("Página {}".format(st.session_state.current_page))
st.divider()
user_input = st.chat_input("Mensaje...")

# Enviar mensajes
if user_input:
    message(st.session_state.current_page, user_input)

# Botón para reconocimiento de voz en tiempo real
if col2.button("Grabar 🎙️", use_container_width=True):
    st.toast("Iniciando reconocimiento de voz...")
    q = queue.Queue()
    thread = threading.Thread(target=voice_recognition_thread, args=(q,))
    thread.start()

    while True:
        result = q.get()
        if result == "Empiece a hablar...":
            st.toast(result)
        elif result == "stop":
            break
        elif "Error:" in result:
            break
        else:
            message(st.session_state.current_page, result)

    thread.join()

show_messages()