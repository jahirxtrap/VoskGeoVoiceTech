from ENGINE.STT.vosk_recog import speech_to_text

try:
    # Iniciar el reconocimiento de voz
    for speech in speech_to_text():
        if speech.strip():  # Asegura que el texto no sea solo espacios
            print("Humano >>", speech)
except KeyboardInterrupt:
    print("\nReconocimiento de voz interrumpido por el usuario.")
except Exception as e:
    print("\nError durante el reconocimiento de voz:", e)
finally:
    print("Finalizando el reconocimiento de voz.")
