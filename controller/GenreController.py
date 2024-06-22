from flask import jsonify, request
from service.GenreService import GenreService


class GenreController:
    def __init__(self, api_key):
        self.genre_service = GenreService(api_key)

    def generate_lyrics_genre_handler(self):
        prompt = request.json.get('prompt')
        genre = request.json.get('genre')
        language = request.json.get('language')
        lyrics = self.genre_service.generate_lyrics_genre(prompt, genre, language)
        return jsonify({'lyrics': lyrics})
