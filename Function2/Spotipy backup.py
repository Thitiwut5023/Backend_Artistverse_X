import spotipy
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

auth_manager = SpotifyClientCredentials('', '')
sp = spotipy.Spotify(auth_manager=auth_manager)


def getTrackIDs(user, playlist_id):
    track_ids = []
    playlist = sp.user_playlist(user, playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        track_ids.append(track['id'])
    return track_ids


def getTrackFeatures(id):
    track_info = sp.track(id)

    name = track_info['name']
    album = track_info['album']['name']
    artist = track_info['album']['artists'][0]['name']
    image = track_info['album']['images'][0]['url'] if track_info['album']['images'] else None
    spotify_link = track_info['external_urls']['spotify']
    # release_date = track_info['album']['release_date']
    # length = track_info['duration_ms']
    # popularity = track_info['popularity']

    track_data = [name, album, artist, image, spotify_link]
    # , release_date, length, popularity
    return track_data


#creating dataframe of feteched playlist
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
music_dist = {0: "609gQW5ztNwAkKnoZplkao", 1: "37i9dQZF1E8O6F3Rlvdl9J", 2: "37i9dQZF1EIfMwRYymgnLH",
              3: "7GhawGpb43Ctkq3PRP1fOL", 4: "0VSM3nkOwwOT89gesFGWcm", 5: "17KV3prdQPa7a38BF0LX2y",
              6: "37i9dQZF1E8NRg7j817gSt"}


track_ids = getTrackIDs('spotify', music_dist[0])
track_list = []
for i in range(len(track_ids)):
    time.sleep(.3)
    track_data = getTrackFeatures(track_ids[i])
    track_list.append(track_data)
    df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artist', 'Image', 'Spotify_link']) # ,'Release_date','Length','Popularity'
    df.to_csv('songs/angry.csv')
print("CSV Generated")

track_ids = getTrackIDs('spotify', music_dist[1])
track_list = []
for i in range(len(track_ids)):
    time.sleep(.3)
    track_data = getTrackFeatures(track_ids[i])
    track_list.append(track_data)
    df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artist', 'Image', 'Spotify_link']) # ,'Release_date','Length','Popularity'
    df.to_csv('songs/disgusted.csv')
print("CSV Generated")

track_ids = getTrackIDs('spotify', music_dist[2])
track_list = []
for i in range(len(track_ids)):
    time.sleep(.3)
    track_data = getTrackFeatures(track_ids[i])
    track_list.append(track_data)
    df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artist', 'Image', 'Spotify_link']) # ,'Release_date','Length','Popularity'
    df.to_csv('songs/fearful.csv')
print("CSV Generated")

track_ids = getTrackIDs('spotify', music_dist[3])
track_list = []
for i in range(len(track_ids)):
    time.sleep(.3)
    track_data = getTrackFeatures(track_ids[i])
    track_list.append(track_data)
    df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artist', 'Image', 'Spotify_link']) # ,'Release_date','Length','Popularity'
    df.to_csv('songs/happy.csv')
print("CSV Generated")

track_ids = getTrackIDs('spotify', music_dist[4])
track_list = []
for i in range(len(track_ids)):
    time.sleep(.3)
    track_data = getTrackFeatures(track_ids[i])
    track_list.append(track_data)
    df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artist', 'Image', 'Spotify_link']) # ,'Release_date','Length','Popularity'
    df.to_csv('songs/neutral.csv')
print("CSV Generated")

track_ids = getTrackIDs('spotify', music_dist[5])
track_list = []
for i in range(len(track_ids)):
    time.sleep(.3)
    track_data = getTrackFeatures(track_ids[i])
    track_list.append(track_data)
    df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artist', 'Image', 'Spotify_link']) # ,'Release_date','Length','Popularity'
    df.to_csv('songs/sad.csv')
print("CSV Generated")

track_ids = getTrackIDs('spotify', music_dist[6])
track_list = []
for i in range(len(track_ids)):
    time.sleep(.3)
    track_data = getTrackFeatures(track_ids[i])
    track_list.append(track_data)
    df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artist', ' mage', 'Spotify_link']) # ,'Release_date','Length','Popularity'
    df.to_csv('songs/surprised.csv')
print("CSV Generated")
