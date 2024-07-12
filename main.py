from flask import Flask
from flask_cors import CORS
from controller.GenreController import GenreController
from controller.MoodController import MoodController
from controller.ArtistController import ArtistController
from controller.CameraController import CameraController
from controller.AnalysisController import AnalysisController

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

OPENAI_API_KEY = ""


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

@app.route('/analysis-lyrics', methods=['POST'])
def analysis_lyrics_route():
    analysis_controller = AnalysisController(OPENAI_API_KEY)
    return analysis_controller.analysis_lyrics_handler()
    
if __name__ == '__main__':
    app.run(debug=True)
