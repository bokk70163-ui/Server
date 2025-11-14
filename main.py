import os
from flask import Flask, request, render_template_string, send_from_directory, flash, redirect, url_for
from pytiktokdownloader import TikTokDownloader
import uuid
import secrets

# === AUTO CREATE FOLDERS ===
if not os.path.exists('downloads'):
    os.makedirs('downloads')
if not os.path.exists('templates'):
    os.makedirs('templates')

# === AUTO SECRET KEY ===
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = secrets.token_hex(24)
app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

# === HTML TEMPLATE (Embedded) ===
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TikTok Downloader</title>
  <style>
    body { font-family: Arial; text-align: center; margin-top: 50px; background: #f1f1f1; }
    .container { max-width: 600px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    input[type="text"] { width: 80%; padding: 10px; font-size: 16px; }
    button { padding: 10px 20px; font-size: 16px; background: #fe2c55; color: white; border: none; cursor: pointer; margin: 10px;}
    .success { color: green; margin: 20px 0; }
    .error { color: red; }
    a { text-decoration: none; }
  </style>
</head>
<body>
  <div class="container">
    <h1>TikTok Video Downloader</h1>
    <form method="POST" action="/download">
      <input type="text" name="url" placeholder="Paste TikTok URL here..." required>
      <button type="submit">Download</button>
    </form>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <p class="{{ category }}">{{ message }}</p>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if download_link %}
      <div class="success">
        <p>Video ready!</p>
        <a href="{{ url_for('downloaded_file', filename=download_link) }}" download>
          <button>Download Video</button>
        </a>
      </div>
    {% endif %}
  </div>
</body>
</html>
'''

# === CONFIG ===
app.config['DOWNLOADS_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# === ROUTES ===
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

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
        title = "".join(c for c in (video_info.get('desc', 'video')[:50]) if c.isalnum() or c in ' -_')
        if not title: title = 'video'
        filename = f"{uuid.uuid4().hex}_{title}.mp4"
        filepath = os.path.join(app.config['DOWNLOADS_FOLDER'], filename)

        downloader.download_video(video_url, filepath)

        return render_template_string(HTML_TEMPLATE, download_link=filename, success=True)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/downloads/<filename>')
def downloaded_file(filename):
    return send_from_directory(app.config['DOWNLOADS_FOLDER'], filename)

# === RUN ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
