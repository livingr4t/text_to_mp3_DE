from flask import Flask, request, send_file, render_template
from gtts import gTTS
from pydub import AudioSegment
import os

app = Flask(__name__)

# Ręczne ustawienie ścieżek do FFmpeg i FFprobe
AudioSegment.converter = "ffmpeg"
AudioSegment.ffprobe = "ffprobe"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Błąd: Nie przesłano pliku tekstowego!", 400

    file = request.files['file']
    pause = int(request.form.get('pause', 1))  # Pauza między zdaniami w sekundach

    try:
        content = file.read().decode('utf-8')
        sentences = [sentence.strip() for sentence in content.split('.') if sentence.strip()]

        combined_audio = AudioSegment.empty()

        for sentence in sentences:
            tts = gTTS(sentence, lang='de')
            tts.save("temp.mp3")
            audio = AudioSegment.from_file("temp.mp3")
            combined_audio += audio
            combined_audio += AudioSegment.silent(duration=pause * 1000)

        output_file = "output.mp3"
        combined_audio.export(output_file, format="mp3")
        os.remove("temp.mp3")

        return send_file(output_file, as_attachment=True)

    except FileNotFoundError as e:
        return f"Błąd: Nie znaleziono FFmpeg lub ffprobe. Szczegóły: {str(e)}", 500
    except Exception as e:
        return f"Błąd: Wystąpił nieoczekiwany problem: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
