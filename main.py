from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from camera import VideoCamera
from controller.genre_controller import generate_lyrics_genre_handler
from controller.mood_controller import generate_lyrics_mood_handler
from controller.artist_controller import generate_lyrics_artist_handler

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


df1 = None
emotion = None

headings = ("Name", "Album", "Artist", "Image", "Spotify_link")


def gen(camera):
    global df1, emotion
    while True:
        frame, df1, emotion = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/t')
def gen_table():
    global df1, emotion
    if df1 is not None:
        response = {
            "songs": df1.to_json(orient='records'),
            "emotion": emotion
        }
        return jsonify(response)
    else:
        return jsonify({"songs": [], "emotion": None})


if __name__ == '__main__':
    app.run(debug=True)
