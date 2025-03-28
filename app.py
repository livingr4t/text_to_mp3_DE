from flask import Flask, request, send_file, render_template
from gtts import gTTS
from pydub import AudioSegment
import os

# Initialize Flask app
app = Flask(__name__)

# Manually configure FFmpeg paths
AudioSegment.converter = "ffmpeg"
AudioSegment.ffprobe = "ffprobe"

# Home route to render the website
@app.route('/')
def home():
    return render_template('index.html')  # Ensure this file is in the `templates` folder

# File upload and audio processing route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or not request.files['file']:
        return "Error: No file uploaded!", 400

    file = request.files['file']
    pause = int(request.form.get('pause', 1))

    try:
        # Read file content and split into sentences
        content = file.read().decode('utf-8')
        sentences = [sentence.strip() for sentence in content.split('.') if sentence.strip()]
        if not sentences:
            return "Error: The uploaded file is empty!", 400

        combined_audio = AudioSegment.empty()

        # Generate audio for each sentence
        for sentence in sentences:
            tts = gTTS(sentence, lang='de')  # Generate German speech
            tts.save("temp.mp3")
            audio = AudioSegment.from_file("temp.mp3")
            combined_audio += audio
            combined_audio += AudioSegment.silent(duration=pause * 1000)  # Add silence

        # Save final combined audio
        output_file = "output.mp3"
        combined_audio.export(output_file, format="mp3")
        os.remove("temp.mp3")  # Clean up temporary file

        return send_file(output_file, as_attachment=True)

    except FileNotFoundError as e:
        return f"Error: FFmpeg or FFprobe not found. Details: {str(e)}", 500
    except Exception as e:
        return f"Error: An unexpected issue occurred. Details: {str(e)}", 500

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
