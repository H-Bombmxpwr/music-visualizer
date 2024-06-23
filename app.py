from flask import Flask, request, redirect, session, render_template, jsonify
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import requests

from src.wikipedia import get_wikipedia_info

load_dotenv(dotenv_path='keys.env')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

app = Flask(__name__)
app.secret_key = os.urandom(24)

sp_oauth = SpotifyOAuth(client_id=os.getenv('SPOTIPY_CLIENT_ID'),
                        client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
                        redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
                        scope='user-top-read user-read-recently-played user-read-email user-read-private')

def get_colors(image, numcolors=6, resize=150):
    img = image.copy()
    img.thumbnail((resize, resize))
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=numcolors)
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    colors = []
    
    num_colors_to_return = min(numcolors, len(color_counts))
    
    for i in range(num_colors_to_return):
        palette_index = color_counts[i][1]
        dominant_color = palette[palette_index*3:palette_index*3+3]
        colors.append(tuple(dominant_color))

    return colors

def get_dominant_and_contrast_colors(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img = img.convert('RGB')
    colors = get_colors(img)
    
    if len(colors) < 2:
        return '#000000', '#FFFFFF'  # Fallback colors

    dominant_color = colors[0]
    contrast_color = get_contrasting_color(dominant_color)
    
    # Find the color with the most contrast
    max_contrast = 0
    best_contrast_color = contrast_color
    for color in colors[1:]:
        contrast = get_contrast_ratio(dominant_color, color)
        if contrast > max_contrast:
            max_contrast = contrast
            best_contrast_color = '#{:02x}{:02x}{:02x}'.format(*color)
    
    return '#{:02x}{:02x}{:02x}'.format(*dominant_color), best_contrast_color

def get_contrasting_color(rgb_color):
    brightness = (299 * rgb_color[0] + 587 * rgb_color[1] + 114 * rgb_color[2]) / 1000
    return '#000000' if brightness > 128 else '#FFFFFF'

def get_contrast_ratio(color1, color2):
    luminance1 = (0.2126 * color1[0] + 0.7152 * color1[1] + 0.0722 * color1[2]) / 255
    luminance2 = (0.2126 * color2[0] + 0.7152 * color2[1] + 0.0722 * color2[2]) / 255
    if luminance1 > luminance2:
        return (luminance1 + 0.05) / (luminance2 + 0.05)
    else:
        return (luminance2 + 0.05) / (luminance1 + 0.05)

@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code, as_dict=False)
    session["token_info"] = token_info
    sp = spotipy.Spotify(auth=token_info)
    user = sp.current_user()
    session['user_name'] = user['display_name']
    session['user_image'] = user['images'][0]['url'] if user['images'] else None
    return redirect('/collage')

@app.route('/collage')
def create_collage():
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info)
    results = sp.current_user_top_tracks(limit=50, time_range='short_term')

    albums_info = []
    
    for item in results['items']:
        album = item['album']
        dominant_color, text_color = get_dominant_and_contrast_colors(album['images'][0]['url'])
        album_info = {
            'name': album['name'],
            'artist': album['artists'][0]['name'],
            'image_url': album['images'][0]['url'],
            'release_year': album['release_date'].split('-')[0],
            'most_listened_track': item['name'],
            'dominant_color': dominant_color,
            'text_color': text_color
        }
        albums_info.append(album_info)

    albums_info.sort(key=lambda x: x['most_listened_track'], reverse=True)  # Sort by most listened to track

    return render_template('collage.html', albums=albums_info, user_name=session.get('user_name'), user_image=session.get('user_image'))

@app.route('/get_wikipedia_info', methods=['POST'])
def get_wikipedia_info_endpoint():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    info = get_wikipedia_info(query)
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
