from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for
import os
from pytiktokdownloader import TikTokDownloader
import uuid

app = Flask(__name__)
app.secret_key = '1f3099648340e2ad6c43098b8a529f18'
app.config['DOWNLOADS_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max

# Ensure download folder exists
os.makedirs(app.config['DOWNLOADS_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url or 'tiktok.com' not in url:
        flash('Invalid TikTok URL!', 'error')
        return redirect(url_for('index'))

    try:
        downloader = TikTokDownloader()
        video_info = downloader.get_video_info(url)
        
        if not video_info or 'playAddr' not in video_info:
            flash('Could not fetch video. Try another link.', 'error')
            return redirect(url_for('index'))

        video_url = video_info['playAddr'][0]
        title = video_info.get('desc', 'tiktok_video')[:50]
        filename = f"{uuid.uuid4().hex}_{title}.mp4"
        filepath = os.path.join(app.config['DOWNLOADS_FOLDER'], filename)

        # Download video
        downloader.download_video(video_url, filepath)

        return render_template('index.html', download_link=filename, success=True)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/downloads/<filename>')
def downloaded_file(filename):
    return send_from_directory(app.config['DOWNLOADS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
