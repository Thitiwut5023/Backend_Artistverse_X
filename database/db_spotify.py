import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
import requests
from database.db_connection import create_connection, close_connection

auth_manager = SpotifyClientCredentials('', '')
sp = spotipy.Spotify(auth_manager=auth_manager)

db_connection = create_connection()
cursor = db_connection.cursor()

def truncate_table():
    cursor.execute("TRUNCATE TABLE spotify_track")
    db_connection.commit()

truncate_table()

def getTrackIDs(user, playlist_id):
    track_ids = []
    playlist = sp.user_playlist(user, playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        track_ids.append(track['id'])
    return track_ids

def getTrackFeatures(id, emotion, retries=5, backoff_factor=1):
    for attempt in range(retries):
        try:
            track_info = sp.track(id)
            name = track_info['name']
            album = track_info['album']['name']
            artist = track_info['album']['artists'][0]['name']
            image = track_info['album']['images'][0]['url'] if track_info['album']['images'] else None
            spotify_link = track_info['external_urls']['spotify']
            track_data = (name, album, artist, image, spotify_link, emotion)
            return track_data
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt < retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))  # Exponential backoff
            else:
                raise
        except spotipy.exceptions.SpotifyException as e:
            print(f"Spotify API error: {e}")
            break

def insertTrackData(track_data):
    insert_query = """
    INSERT INTO spotify_track (name, album, artist, image, spotify_link, emotion)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, track_data)
    db_connection.commit()

emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
music_dist = {0: "609gQW5ztNwAkKnoZplkao", 1: "37i9dQZF1E8O6F3Rlvdl9J", 2: "37i9dQZF1EIfMwRYymgnLH",
              3: "7GhawGpb43Ctkq3PRP1fOL", 4: "0VSM3nkOwwOT89gesFGWcm", 5: "17KV3prdQPa7a38BF0LX2y",
              6: "37i9dQZF1E8NRg7j817gSt"}

for emotion, playlist_id in music_dist.items():
    track_ids = getTrackIDs('spotify', playlist_id)
    for track_id in track_ids:
        time.sleep(0.3)
        try:
            track_data = getTrackFeatures(track_id, emotion_dict[emotion])
            if track_data:
                insertTrackData(track_data)
        except Exception as e:
            print(f"Failed to fetch or insert track data for {track_id}: {e}")
    print(f"Data for {emotion_dict[emotion]} playlist inserted into the database.")

cursor.close()
close_connection(db_connection)
