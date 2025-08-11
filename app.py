from flask import Flask, render_template, request, jsonify, send_from_directory
from pytubefix import YouTube
import os
import subprocess
import logging
import json
from typing import Tuple

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

folder_path = 'static/videos'


if not os.path.exists(folder_path):
    os.makedirs(folder_path)
else:
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def po_token_verifier() -> Tuple[str, str]:
    # This function calls the command-line tool to get a new token
    result = subprocess.run("youtube-po-token-generator", check=True, shell=True, capture_output=True, text=True)
    token_object = json.loads(result.stdout)
    return token_object["visitorData"], token_object["poToken"]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    start_time = request.json.get('start_time')
    end_time = request.json.get('end_time')
    quality = request.json.get('quality', 'best')
    video_format = request.json.get('format', 'mp4')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        yt = YouTube(url,
                     use_po_token=True,
                     po_token_verifier=po_token_verifier)
        audio = yt.streams.filter(only_audio=True).first()
        stream = yt.streams.filter(adaptive=True, resolution=quality).first()

        if not stream:
            return jsonify({'error': f'No stream found for quality: {quality}'}), 404

        original_filename = stream.download(output_path=folder_path)
        original_audio = audio.download(output_path=folder_path)
        base, ext = os.path.splitext(original_filename)

        if video_format == 'audio':
            output_filename = f'{base}_cropped.mp3'
            ffmpeg_command = [
                'ffmpeg',
                '-i', original_audio,
                '-ss', str(start_time),
                '-to', str(end_time),
                '-c:a', 'libmp3lame',
                '-q:a', '2',
                output_filename
            ]
        else:
            output_filename = f'{base}_cropped.mp4'
            ffmpeg_command = [
                'ffmpeg',
                '-i', original_filename,
                '-i', original_audio,
                '-ss', str(start_time),
                '-to', str(end_time),
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-strict', 'experimental',
                output_filename
            ]

        subprocess.run(ffmpeg_command, check=True)

        os.remove(original_filename)
        os.remove(original_audio)

        filename = os.path.basename(output_filename)
        return jsonify({'message': 'Download successful!', 'filename': filename})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('static/videos', filename)

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        yt = YouTube(url,
                     use_po_token=True,
                     po_token_verifier=po_token_verifier)
        streams = yt.streams.filter(adaptive=True, file_extension='mp4').order_by('resolution').desc()

        qualities = set()
        for stream in streams:
            if stream.resolution and int(stream.resolution[:-1]) <= 1080:
                qualities.add(stream.resolution)

        sorted_qualities = sorted(list(qualities), key=lambda x: int(x[:-1]), reverse=True)

        return jsonify({
            'qualities': [{'quality': q, 'format_id': q} for q in sorted_qualities],
            'duration': yt.length
        })

    except Exception as e:
        app.logger.error(f"Error getting video info for url: {url} - {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)