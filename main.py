from flask import Flask
from flask_cors import CORS
from controller.genre_controller import generate_lyrics_genre_handler
from controller.mood_controller import generate_lyrics_mood_handler
from controller.artist_controller import generate_lyrics_artist_handler
from controller.camera_controller import video_feed, gen_table

app = Flask(__name__)

app.config.from_object(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/generate-lyrics-genre', methods=['POST'])
def generate_lyrics_genre_route():
    return generate_lyrics_genre_handler()


@app.route('/generate-lyrics-mood', methods=['POST'])
def generate_lyrics_mood_route():
    return generate_lyrics_mood_handler()


@app.route('/generate-lyrics-artist', methods=['POST'])
def generate_lyrics_artist_route():
    return generate_lyrics_artist_handler()


@app.route('/video_feed')
def video_feed_route():
    return video_feed()


@app.route('/t')
def gen_table_route():
    return gen_table()


# previous_response = ""
#
#
# @app.route('/ai-assistance', methods=['POST'])
# def ai_assistance():
#     global previous_response
#     prompt = request.json.get('prompt')
#
#     if not previous_response:
#         music_info_prompt = f"Extract musical information from the given lyrics and give me Chord,Keys,Time signature and tempo that suit this lyrics:\nUser: {prompt}\n"
#     else:
#         music_info_prompt = f"User: {previous_response}\nAI: {prompt}"
#
#     # Generate a response using OpenAI GPT-3.5
#     completion = openai_client.chat.completions.create(
#         model="gpt-3.5-turbo-1106",
#         messages=[
#             {"role": "system", "content": ""},
#             {"role": "user", "content": music_info_prompt}
#         ]
#     )
#
#     response = completion.choices[0].message.content.strip()
#
#     previous_response = response
#
#     return jsonify({'response': response})


if __name__ == '__main__':
    app.run(debug=True)
