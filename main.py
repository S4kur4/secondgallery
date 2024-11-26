from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, session
import os
import random
import uuid
import json
import secrets
from functools import wraps
from PIL import Image
import io

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['PHOTO_FOLDER'] = os.path.join(app.static_folder, 'photos')

USERNAME = os.environ.get('ADMIN_USERNAME')
PASSWORD = os.environ.get('ADMIN_PASSWORD')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    social_configs = [
        {
            'icon': 'fa-facebook-f',
            'env_key': 'FACEBOOK_URL'
        },
        {
            'icon': 'fa-instagram',
            'env_key': 'INSTAGRAM_URL'
        },
        {
            'icon': 'fa-x-twitter',
            'env_key': 'X_URL'
        },
        {
            'icon': 'fa-linkedin-in',
            'env_key': 'LINKEDIN_URL'
        },
        {
            'icon': 'fa-telegram',
            'env_key': 'TELEGRAM_URL'
        },
        {
            'icon': 'fa-discord',
            'env_key': 'DISCORD_URL'
        },
        {
            'icon': 'fa-behance',
            'env_key': 'BEHANCE_URL'
        },
        {
            'icon': 'fa-youtube',
            'env_key': 'YOUTUBE_URL'
        },
        {
            'icon': 'fa-pinterest',
            'env_key': 'PINTEREST_URL'
        }
    ]
    tittle = os.environ.get('TITTLE')
    social_links = []
    for config in social_configs:
        url = os.environ.get(config['env_key'])
        if url:
            social_links.append({
                'icon': config['icon'],
                'url': url
            })
    about_me = json.loads(os.environ.get('ABOUT_ME'))
    return render_template('index.html', tittle=tittle, social_links=social_links, about_me=about_me)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('manage'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


@app.route('/manage')
@login_required
def manage():
    return render_template('manage.html')


@app.route('/api/photo_list')
def photo_list():
    photos = [f for f in os.listdir(app.config['PHOTO_FOLDER'])
              if f.lower().endswith(('.webp',))
              and not f.endswith('-thumbnail.webp')]
    return jsonify(photos)


@app.route('/static/photos/<path:filename>')
def serve_photo(filename):
    # Cache for 30 days
    return send_from_directory(app.config['PHOTO_FOLDER'], filename, max_age=604800)


@app.route('/api/delete_photo', methods=['POST'])
@login_required
def delete_photo():
    filename = request.json.get('filename')
    if filename:
        file_path = os.path.join(app.config['PHOTO_FOLDER'], filename)
        thumbnail_path = os.path.join(
            app.config['PHOTO_FOLDER'], filename.replace('.webp', '-thumbnail.webp'))
        deleted = False
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted = True
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            deleted = True
        if deleted:
            return jsonify({'success': True, 'message': 'Photo deleted successfully'})
    return jsonify({'success': False, 'message': 'Failed to delete photo'}), 400


@app.route('/api/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) + '.webp'
        file_path = os.path.join(app.config['PHOTO_FOLDER'], filename)
        thumbnail_path = os.path.join(
            app.config['PHOTO_FOLDER'], filename.replace('.webp', '-thumbnail.webp'))

        # Save and convert to webp
        img = Image.open(file)
        img.save(file_path, 'WEBP')

        # Create thumbnail
        width, height = img.size
        thumbnail_size = (int(width * 0.6), int(height * 0.6))
        img.thumbnail(thumbnail_size)
        img.save(thumbnail_path, 'WEBP')

        return jsonify({'success': True, 'message': 'Photo uploaded successfully', 'filename': filename})
    return jsonify({'success': False, 'message': 'File type not allowed'}), 400


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(debug=True)
