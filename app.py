from flask import Flask, request, send_file, render_template
from gtts import gTTS
from pydub import AudioSegment
import os

app = Flask(__name__)

# Configure paths for FFmpeg and FFprobe
AudioSegment.converter = "ffmpeg"
AudioSegment.ffprobe = "ffprobe"

@app.route('/')
def home():
    # Render the HTML form from templates/index.html
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Validate file upload
        if 'file' not in request.files or not request.files['file']:
            return "Error: No file uploaded!", 400

        file = request.files['file']
        pause = int(request.form.get('pause', 1))  # Get pause duration from form

        # Read file content
        content = file.read().decode('utf-8')
        sentences = [sentence.strip() for sentence in content.split('.') if sentence.strip()]
        if not sentences:
            return "Error: File is empty or not in the correct format!", 400

        combined_audio = AudioSegment.empty()

        # Generate audio for each sentence
        for sentence in sentences:
            tts = gTTS(sentence, lang='de')  # Language: German
            tts.save("temp.mp3")
            audio = AudioSegment.from_file("temp.mp3")
            combined_audio += audio
            combined_audio += AudioSegment.silent(duration=pause * 1000)  # Pause between sentences

        # Export the combined audio file
        output_file = "output.mp3"
        combined_audio.export(output_file, format="mp3")
        os.remove("temp.mp3")  # Clean up temporary file

        return send_file(output_file, as_attachment=True)

    except FileNotFoundError as e:
        return f"Error: FFmpeg or FFprobe not found. Details: {str(e)}", 500
    except Exception as e:
        return f"Error: An unexpected issue occurred: {str(e)}", 500

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
