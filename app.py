from flask import Flask, request, redirect, session, render_template
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import folium
import geopy.geocoders
import os
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path='keys.env')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

app = Flask(__name__)
app.secret_key = os.urandom(24)

sp_oauth = SpotifyOAuth(client_id=os.getenv('SPOTIPY_CLIENT_ID'),
                        client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
                        redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
                        scope='user-top-read')

geolocator = geopy.geocoders.Nominatim(user_agent="music_map")

@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect('/map')

@app.route('/map')
def create_map():
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_top_artists(limit=50, time_range='short_term')

    artist_locations = []
    for artist in results['items']:
        # Attempt to get the artist's hometown from the Spotify API
        # If not available, fallback to geocoding the artist's name
        if 'hometown' in artist and artist['hometown']:
            location = geolocator.geocode(artist['hometown'])
        else:
            location = geolocator.geocode(artist['name'])

        if location:
            artist_locations.append({'name': artist['name'], 'lat': location.latitude, 'lon': location.longitude})
            # Print artist name and location to console
            print(f"Artist: {artist['name']}, Location: ({location.latitude}, {location.longitude})")
        else:
            # Print if location not found
            print(f"Artist: {artist['name']}, Location: Not Found")

    return render_template('map.html', artist_locations=artist_locations)

if __name__ == '__main__':
    app.run(debug=True)
