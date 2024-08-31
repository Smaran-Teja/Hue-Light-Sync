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
song_name = "Die for me"
results = sp.search(q=song_name, limit=1, type="track")
track = results['tracks']['items'][0]

# song details
print(f"Song: {track['name']}")
print(f"Artist: {track['artists'][0]['name']}")
print(f"URI: {track['uri']}")

# first active device
devices = sp.devices()
device_id = None
if devices['devices']:
    device_id = devices['devices'][0]['id']
    print(f"Device ID: {device_id}")


#audio analysis/beats for the track
track_id = track['id']
analysis = sp.audio_analysis(track_id)
beats = analysis['beats']
segments = analysis['segments']

loudness_tracker = {}
for i, segment in enumerate(segments[:]):  
    start = segment['start']
    #duration = segment['duration']
    loudness = segment['loudness_start']
    #print(f"Segment {i + 1}: Start={start}, Duration={duration}, Loudness={loudness}")

    loudness_tracker[start] = loudness

loudness_tracker = dict(sorted(loudness_tracker.items()))

prev_loud = 0
def get_loudness_as_brightness(pos):
    for start in loudness_tracker:
        if start > pos:
            return (prev_loud + 60) * 2.125
        prev_loud = loudness_tracker[start]
    return prev_loud

print(f"Total Beats: {len(beats)}")
#for i, beat in enumerate(beats[:]): 
#    start = beat['start']
#    confidence = beat['confidence']
#    duration = beat["duration"]
#    print(f"Beat {i + 1}: Start={start}, Confidence={confidence}, Duration: {duration}")



# play song
if device_id:
    sp.start_playback(device_id=device_id, uris=[track['uri']], position_ms = 0)
else:
    print("No active device found. Please play a song on your Spotify app to activate a device.")