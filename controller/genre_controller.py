from flask import jsonify, request
from service.genre_service import generate_lyrics_genre


def generate_lyrics_genre_handler():
    prompt = request.json.get('prompt')
    genre = request.json.get('genre')
    language = request.json.get('language')
    lyrics = generate_lyrics_genre(prompt, genre, language)
    return jsonify({'lyrics': lyrics})