import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

#Spotify app credentials from .env file (gitignored)
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
redirect_uri = os.environ["REDIRECT_URI"]

# client access scope
scope = 'user-modify-playback-state user-read-playback-state'

# spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

# song search
song_name = "i met you when i was 18"
results = sp.search(q=song_name, limit=1, type="album")
album = results['albums']['items'][0]

# song details
print(f"Album: {album['name']}")
print(f"Artist: {album['artists'][0]['name']}")
print(f"URI: {album['uri']}")

# first active device
devices = sp.devices()
device_id = None
if devices['devices']:
    device_id = devices['devices'][0]['id']
    print(f"Device ID: {device_id}")

# play song
if device_id:
    sp.start_playback(device_id=device_id, context_uri=album['uri'], position_ms = 2000)
else:
    print("No active device found. Please play a song on your Spotify app to activate a device.")
