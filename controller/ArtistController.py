from flask import jsonify, request
from service.ArtistService import ArtistService


class ArtistController:
    def __init__(self, api_key):
        self.artist_service = ArtistService(api_key)

    def generate_lyrics_artist_handler(self):
        prompt = request.json.get('prompt')
        artist = request.json.get('artist')
        language = request.json.get('language')
        lyrics = self.artist_service.generate_lyrics_artist(prompt, artist, language)
        return jsonify({'lyrics': lyrics})
