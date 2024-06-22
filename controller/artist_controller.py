from flask import jsonify, request
from service.artist_service import generate_lyrics_artist


def generate_lyrics_artist_handler():
    prompt = request.json.get('prompt')
    artist = request.json.get('artist')
    language = request.json.get('language')
    lyrics = generate_lyrics_artist(prompt, artist, language)
    return jsonify({'lyrics': lyrics})
