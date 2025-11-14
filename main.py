import os
from flask import Flask, request, render_template_string, send_from_directory, flash, redirect, url_for
import yt_dlp
import uuid
import secrets

# === AUTO FOLDERS ===
os.makedirs('downloads', exist_ok=True)

# === SECRET KEY ===
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = secrets.token_hex(24)

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
app.config['DOWNLOADS_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# === HTML ===
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TikTok Downloader</title>
<style>
  body {font-family: Arial; text-align: center; margin-top: 50px; background: #f1f1f1;}
  .container {max-width: 600px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);}
  input[type="text"] {width: 80%; padding: 10px; font-size: 16px;}
  button {padding: 10px 20px; font-size: 16px; background: #fe2c55; color: white; border: none; cursor: pointer; margin: 10px;}
  .success {color: green; margin: 20px 0;} .error {color: red;}
</style>
</head><body>
<div class="container">
  <h1>TikTok Downloader</h1>
  <form method="POST" action="/download">
    <input type="text" name="url" placeholder="Paste TikTok URL..." required>
    <button type="submit">Download</button>
  </form>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}{% for c, m in messages %}<p class="{{c}}">{{m}}</p>{% endfor %}{% endif %}
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
</body></html>
'''

# === DOWNLOAD FUNCTION ===
def download_video(url, filepath):
    ydl_opts = {
        'outtmpl': filepath,
        'format': 'best[height<=720][ext=mp4]',
        'quiet': True,
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

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
        filename = f"{uuid.uuid4().hex}_video.mp4"
        filepath = os.path.join(app.config['DOWNLOADS_FOLDER'], filename)
        download_video(url, filepath)
        return render_template_string(HTML_TEMPLATE, download_link=filename)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/downloads/<filename>')
def downloaded_file(filename):
    return send_from_directory(app.config['DOWNLOADS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
