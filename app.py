from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os
import subprocess

app = Flask(__name__)

# Ensure the static/videos directory exists
if not os.path.exists('static/videos'):
    os.makedirs('static/videos')

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
        ydl_opts = {
            'outtmpl': f'static/videos/%(title)s.%(ext)s',
        }

        if video_format == 'mp3':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if quality == 'best':
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
            else:
                format_height = quality.replace('p', '')  # Convert "720p" to "720"
                ydl_opts['format'] = f'bestvideo[height<={format_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={format_height}]'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            original_filename = info.get('requested_downloads')[0]['filepath']

        base, ext = os.path.splitext(original_filename)
        output_filename = f'{base}_cropped.{video_format}'

        ffmpeg_command = [
            'ffmpeg',
            '-i', original_filename,
            '-ss', str(start_time),
            '-to', str(end_time),
            '-c', 'copy' if video_format != 'mp3' else 'libmp3lame',
            output_filename
        ]

        if video_format == 'avi':
            ffmpeg_command[-3] = 'libxvid'

        subprocess.run(ffmpeg_command, check=True)

        os.remove(original_filename)
        
        # Get just the filename without the full path
        filename = os.path.basename(output_filename)
        return jsonify({'message': 'Download successful!', 'filename': filename})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('static/videos', filename)

@app.route('/get-qualities', methods=['POST'])
def get_qualities():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Filter and process video formats
            video_qualities = set()  # Use set to avoid duplicates
            qualities = []
            
            for f in formats:
                height = f.get('height')
                if height and f.get('vcodec') != 'none':  # Only video formats
                    quality = f"{height}p"
                    if quality not in video_qualities and height <= 1080:  # Limit to 1080p
                        video_qualities.add(quality)
                        qualities.append({
                            'format_id': f['format_id'],
                            'quality': quality
                        })
            
            # Sort by height descending
            qualities.sort(key=lambda x: int(x['quality'][:-1]), reverse=True)
            
            # Add "best" quality option
            qualities.insert(0, {
                'format_id': 'best',
                'quality': 'Best'
            })
            
            return jsonify({'qualities': qualities})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({'duration': info.get('duration')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
