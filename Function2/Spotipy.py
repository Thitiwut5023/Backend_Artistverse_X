import spotipy
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from Database.db_connection import create_connection, close_connection


# Spotify authentication
auth_manager = SpotifyClientCredentials('', '')
sp = spotipy.Spotify(auth_manager=auth_manager)

# Get database connection
db_connection = create_connection()
cursor = db_connection.cursor()

# Truncate the spotify_track table
def truncate_table():
    cursor.execute("TRUNCATE TABLE spotify_track")
    db_connection.commit()

truncate_table()  # Truncate table before inserting new data

def getTrackIDs(user, playlist_id):
    track_ids = []
    playlist = sp.user_playlist(user, playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        track_ids.append(track['id'])
    return track_ids

def getTrackFeatures(id, emotion):
    track_info = sp.track(id)

    name = track_info['name']
    album = track_info['album']['name']
    artist = track_info['album']['artists'][0]['name']
    image = track_info['album']['images'][0]['url'] if track_info['album']['images'] else None
    spotify_link = track_info['external_urls']['spotify']

    track_data = (name, album, artist, image, spotify_link, emotion)
    return track_data

def insertTrackData(track_data):
    insert_query = """
    INSERT INTO spotify_track (name, album, artist, image, spotify_link, emotion)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, track_data)
    db_connection.commit()

# Playlist IDs for different emotions
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
music_dist = {0: "609gQW5ztNwAkKnoZplkao", 1: "37i9dQZF1E8O6F3Rlvdl9J", 2: "37i9dQZF1EIfMwRYymgnLH",
              3: "7GhawGpb43Ctkq3PRP1fOL", 4: "0VSM3nkOwwOT89gesFGWcm", 5: "17KV3prdQPa7a38BF0LX2y",
              6: "37i9dQZF1E8NRg7j817gSt"}

# Fetch and store track data for each emotion
for emotion, playlist_id in music_dist.items():
    track_ids = getTrackIDs('spotify', playlist_id)
    for track_id in track_ids:
        time.sleep(0.3)
        track_data = getTrackFeatures(track_id, emotion_dict[emotion])
        insertTrackData(track_data)
    print(f"Data for {emotion_dict[emotion]} playlist inserted into the database.")

# Close the database connection
cursor.close()
close_connection(db_connection)