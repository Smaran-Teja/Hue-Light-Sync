import time
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

#Spotify api credentials from .env file (gitignored)
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




# Philips hue api credentials from .env file (gitignored)
bridge_ip = os.environ["BRIDGE_IP"]
api_username = os.environ["API_USERNAME"]
light_id = "5"  # whichever _single_ light to control

# xy coordinates for the desired color (CIE 1931 color space)
xy_color = [0.7, 0.27]


# Prepare the URL and the data payload
url = f"http://{bridge_ip}/api/{api_username}/lights/{light_id}/state"
data = {
    "on": True,             # Turn the light on (optional if already on)
    "xy": xy_color,         # Set the color
    "transition-time": 0,   # Transition time in deciseconds (10 = 1 second)
    "bri": 100
}


BREATHING_TIME = 0.2
CALL_TIME = 0.1
make_call = False
clock = 0
# Send the PUT request
for i in range(len(beats)):
    confidence = beats[i]["confidence"]
    duration = beats[i]["duration"]
    default_brightness = get_loudness_as_brightness(clock)

    print(confidence)
    print(duration)
    print(default_brightness)
    

    if (duration > 0.35):
        make_call = True
        brightness = int(confidence * default_brightness * 3)
        data["bri"] = 255 if brightness>255 else brightness
        response = requests.put(url, json=data)
    
    sleep_time = beats[i]["duration"]
    clock += beats[i]["duration"]
    if make_call:
        clock += CALL_TIME
        sleep_time -= CALL_TIME

    time.sleep(sleep_time)
    

    if make_call:
        data["bri"] = 30 # reset to default
        response = requests.put(url, json=data)
        time.sleep(BREATHING_TIME - CALL_TIME)
        clock += CALL_TIME
        clock +=BREATHING_TIME
    
    else:
        clock += BREATHING_TIME
        time.sleep(BREATHING_TIME)
    
    make_call = False
