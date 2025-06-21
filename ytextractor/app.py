from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Create a directory to store temporary audio files
if not os.path.exists('temp'):
    os.makedirs('temp')

@app.route('/extract', methods=['POST'])
def extract_audio():
    data = request.get_json()
    url = data.get('url')
    start_time = data.get('start') # e.g., "30:00"

    if not url or not start_time:
        return jsonify({"error": "Missing 'url' or 'start' parameter"}), 400

    try:
        # Generate a unique filename to avoid conflicts
        unique_id = str(uuid.uuid4())
        output_filename = os.path.join('temp', f'{unique_id}.mp3')

        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'download_ranges': yt_dlp.utils.download_range_func(None, [(yt_dlp.utils.parse_time(start_time), None)]),
        }

        # Download and extract the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'untitled')

        # Send the file back to the client
        return send_file(output_filename, as_attachment=True, download_name=f'{title}_segment.mp3')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 