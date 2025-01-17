import os
import random
import uuid
import json
import secrets
import io
import hashlib
import requests
from functools import wraps
from PIL import Image
from datetime import datetime
from urllib.parse import urljoin
from flask import make_response
from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['PHOTO_FOLDER'] = os.path.join(app.static_folder, 'photos')

USERNAME = os.environ.get('ADMIN_USERNAME')
PASSWORD = os.environ.get('ADMIN_PASSWORD')
TURNSTILE_SITE_KEY = os.environ.get('TURNSTILE_SITE_KEY')
TURNSTILE_SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY')

def verify_turnstile(token):
     data = {
         "secret": TURNSTILE_SECRET_KEY,
         "response": token
     }
     response = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data)
     return response.json()["success"]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml"""
    pages = []
    base_url = request.url_root.rstrip('/')

    pages.append({
        'loc': base_url,
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'daily',
        'priority': '1.0'
    })

    pages.append({
            'loc': urljoin(base_url, '#about'),
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.8'
    })

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        xml += '  <url>\n'
        xml += f'    <loc>{page["loc"]}</loc>\n'
        xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += '  </url>\n'

    xml += '</urlset>'

    response = make_response(xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@app.route('/robots.txt')
def robots():
    """Generate robots.txt"""
    base_url = request.url_root.rstrip('/')

    robots_txt = f"""User-agent: *
Allow: /
Allow: /static/photos/
Disallow: /login
Disallow: /manage
Disallow: /api/
Disallow: /logout

Sitemap: {base_url}/sitemap.xml
"""

    response = make_response(robots_txt)
    response.headers["Content-Type"] = "text/plain"

    return response


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
            'icon': 'fa-weibo',
            'env_key': 'WEIBO_URL'
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
        },
        {
            'icon': 'fa-github',
            'env_key': 'GITHUB_URL'
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
    google_analytics_id = os.environ.get('GOOGLE_ANALYTICS_ID')
    umami_website_id = os.environ.get('UMAMI_WEBSITE_ID')
    return render_template('index.html', tittle=tittle, social_links=social_links, about_me=about_me, google_analytics_id=google_analytics_id, umami_website_id=umami_website_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if TURNSTILE_SITE_KEY and TURNSTILE_SECRET_KEY:
            turnstile_response = request.form.get('cf-turnstile-response')
            if not turnstile_response:
                return render_template('login.html',
                                    error='Please complete the Turnstile challenge',
                                    turnstile_site_key=TURNSTILE_SITE_KEY)

            if not verify_turnstile(turnstile_response):
                return render_template('login.html',
                                    error='Turnstile verification failed',
                                    turnstile_site_key=TURNSTILE_SITE_KEY)

        if (request.form['username'] == USERNAME and
            hashlib.sha256(request.form['password'].encode()).hexdigest() == PASSWORD):
            session['logged_in'] = True
            return redirect(url_for('manage'))
        else:
            return render_template('login.html',
                                error='Invalid credentials',
                                turnstile_site_key=TURNSTILE_SITE_KEY)
    return render_template('login.html', turnstile_site_key=TURNSTILE_SITE_KEY)


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
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run()
