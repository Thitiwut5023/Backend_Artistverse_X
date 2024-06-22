from flask import jsonify, request
from service.MoodService import MoodService


class MoodController:
    def __init__(self, api_key):
        self.mood_service = MoodService(api_key)

    def generate_lyrics_mood_handler(self):
        prompt = request.json.get('prompt')
        mood = request.json.get('mood')
        language = request.json.get('language')
        lyrics = self.mood_service.generate_lyrics_mood(prompt, mood, language)
        return jsonify({'lyrics': lyrics})
