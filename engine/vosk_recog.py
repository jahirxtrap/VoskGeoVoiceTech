from typing import Generator
import pyaudio
from vosk import Model, KaldiRecognizer
import json

def speech_to_text(prints: bool = True, model_path: str = "./model/vosk-model-small-es-0.42", device_index: int = 1) -> Generator[str, None, None]:
    # Inicializar modelo y reconocedor de voz
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    print("Modelo Inicializado...")

    # Configurar y comenzar la transmisión de audio
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192, input_device_index=device_index)
    stream.start_stream()

    try:
        while True:
            data = stream.read(8192, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                result_dict = json.loads(result)  # Uso de json para un manejo más seguro y claro
                if 'text' in result_dict:
                    transcript = result_dict['text'].lower()
                    if prints: print(f"\rTranscripción: {transcript}")
                    yield transcript
            else:
                partial_result = json.loads(recognizer.PartialResult())
                if prints and "partial" in partial_result:
                    print(f"\rHablando: {partial_result['partial']}", end='', flush=True)
    finally:
        # Limpiar recursos al finalizar
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    for speech in speech_to_text():
        if "stop" in speech:
            print("Diciendo: ", speech)
            print("Aqui acabe chauuu ...")
            break
