from flask import Flask
from flask_cors import CORS
from controller.GenreController import GenreController
from controller.MoodController import MoodController
from controller.ArtistController import ArtistController
from controller.CameraController import CameraController
from controller.AnalysisController import AnalysisController
from controller.SpotifyAuthController import SpotifyAuthController
from controller.SpotifyRecommendController import SpotifyRecommendController
from controller.SearchController import SearchController

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(app, resources={r"/*": {"origins": "*"}})

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route('/generate-lyrics-genre', methods=['POST'])
def generate_lyrics_genre_route():
    genre_controller = GenreController(OPENAI_API_KEY)
    return genre_controller.generate_lyrics_genre_handler()

@app.route('/generate-lyrics-mood', methods=['POST'])
def generate_lyrics_mood_route():
    mood_controller = MoodController(OPENAI_API_KEY)
    return mood_controller.generate_lyrics_mood_handler()

@app.route('/generate-lyrics-artist', methods=['POST'])
def generate_lyrics_artist_route():
    artist_controller = ArtistController(OPENAI_API_KEY)
    return artist_controller.generate_lyrics_artist_handler()

@app.route('/video_feed')
def video_feed_route():
    camera_controller = CameraController()
    return camera_controller.video_feed()

@app.route('/t')
def gen_table_route():
    camera_controller = CameraController()
    return camera_controller.gen_table()

@app.route('/ai-assistance', methods=['POST'])
def analysis_lyrics_route():
    analysis_controller = AnalysisController(OPENAI_API_KEY)
    return analysis_controller.analysis_lyrics_handler()

# Spotify Authentication Routes
@app.route('/auth/spotify/login', methods=['GET'])
def spotify_login():
    spotify_auth_controller = SpotifyAuthController()
    return spotify_auth_controller.get_login_url()

@app.route('/auth/spotify/callback', methods=['GET'])
def spotify_callback():
    spotify_auth_controller = SpotifyAuthController()
    return spotify_auth_controller.handle_callback()

@app.route('/auth/spotify/refresh', methods=['POST'])
def spotify_refresh_token():
    spotify_auth_controller = SpotifyAuthController()
    return spotify_auth_controller.refresh_token()

@app.route('/auth/spotify/profile', methods=['GET'])
def spotify_profile():
    spotify_auth_controller = SpotifyAuthController()
    return spotify_auth_controller.get_user_profile()

@app.route('/auth/spotify/validate', methods=['GET'])
def spotify_validate():
    spotify_auth_controller = SpotifyAuthController()
    return spotify_auth_controller.validate_token()

# Spotify Recommendation Routes
@app.route('/spotify/recommend', methods=['POST'])
def spotify_recommend():
    spotify_recommend_controller = SpotifyRecommendController()
    return spotify_recommend_controller.get_recommendations()

@app.route('/spotify/generate-content', methods=['POST'])
def spotify_generate_content():
    spotify_recommend_controller = SpotifyRecommendController()
    return spotify_recommend_controller.generate_song_content()

# Search Routes
@app.route('/search', methods=['GET'])
def search_route():
    search_controller = SearchController()
    return search_controller.search_handler()

if __name__ == '__main__':
    app.run(debug=True)
