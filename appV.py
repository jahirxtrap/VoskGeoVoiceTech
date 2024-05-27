import streamlit as st
from ENGINE.STT.vosk_recog import speech_to_text
import threading
import queue

def voice_recognition_thread(q, model_path="ASSETS/Vosk/vosk-model-small-es-0.3"):
    try:
        q.put("Modelo inicializando, por favor espera...")
        # Usar un modelo más pequeño y ligero si está disponible
        for speech in speech_to_text(prints=False, model_path=model_path, device_index=1):
            q.put(speech)
            if "stop" in speech or "parate" in speech:  # Detectar "parate" para detener
                q.put("stop")
                break
    except Exception as e:
        q.put(f"Error: {str(e)}")
        q.put("stop")

def main():
    st.title("Reconocimiento de voz en tiempo real")

    if st.button('Iniciar Reconocimiento de Voz'):
        q = queue.Queue()
        thread = threading.Thread(target=voice_recognition_thread, args=(q,))
        thread.start()

        placeholder = st.empty()
        placeholder.info("Cargando modelo de voz...")

        while True:
            result = q.get()
            if result == "Modelo inicializando, por favor espera...":
                placeholder.info(result)
            elif result == "stop":
                placeholder.success("Reconocimiento de voz detenido.")
                break
            elif "Error:" in result:
                placeholder.error(result)
                break
            else:
                placeholder.markdown(f"**Humano >>** {result}")

        thread.join()

    st.write("Haz clic en el botón para iniciar el reconocimiento de voz.")

if __name__ == "__main__":
    main()
