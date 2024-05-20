from flask import jsonify, request
from service.openai_service import generate_lyrics_mood


def generate_lyrics_mood_handler():
    prompt = request.json.get('prompt')
    mood = request.json.get('mood')
    language = request.json.get('language')
    lyrics = generate_lyrics_mood(prompt, mood, language)
    return jsonify({'lyrics': lyrics})
