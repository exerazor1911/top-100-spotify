import re
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint
import os

URL = "https://www.billboard.com/charts/hot-100/"
PATTERN = r'^\d{4}-\d{2}-\d{2}$'
input_date = ''

while not re.match(PATTERN, input_date):
    input_date = input("Which year do you want to travel to? Type the date in this format: YYYY-MM-DD: ")

response = requests.get(f'{URL}{input_date}')
response.raise_for_status()

hot_100_wp = response.text

soup = BeautifulSoup(hot_100_wp, 'html.parser')
songs = [paragraph.getText().strip() for paragraph in soup.select("li ul li h3")]

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=os.environ.get("CLIENT_ID"),
                    client_secret=os.environ.get("CLIENT_SECRET"),
                    redirect_uri="http://example.com",
                    scope="playlist-modify-private")
)
uid = sp.current_user().get('id')

year = input_date[:4]

song_urls = []

for song in songs:
    query = f'track:{song} year:{year}'

    results = sp.search(q=query, type='track')

    if results:
        try:
            song_urls.append(results.get('tracks').get('items')[0].get('uri'))
        except IndexError:
            print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(
    user=uid, name=f'{input_date} Billboard 100', public=False
)

sp.playlist_add_items(playlist_id=playlist.get('id'), items=song_urls, position=None)
