from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from openai import OpenAI
from camera import VideoCamera
from OpenAI.breaklinefunction import extract_lyrics

app = Flask(__name__)

app.config.from_object(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

OPENAI_API_KEY = ""
openai_client = OpenAI(api_key=OPENAI_API_KEY)


@app.route('/', methods=['GET'])
def greeting():
    return ("Hello World!")


@app.route('/generate-lyrics-genre', methods=['POST'])
def generate_lyrics_genre():
    prompt = request.json.get('prompt')
    genre = request.json.get('genre')
    language = request.json.get('language')
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user",
             "content": f"generate a lyrics that have song topic is {prompt} in {language} language and the genre is {genre}. (just give me only lyrics)"}
        ]
    )
    response = completion.choices[0].message.content
    lyrics = extract_lyrics(response)
    return jsonify({'lyrics': lyrics})


@app.route('/generate-lyrics-mood', methods=['POST'])
def generate_lyrics_mood():
    prompt = request.json.get('prompt')
    mood = request.json.get('mood')
    language = request.json.get('language')
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user",
             "content": f"generate a lyrics that have song topic is {prompt} in {language} language and the mood is {mood}. (just give me only lyrics)"}
        ]
    )
    response = completion.choices[0].message.content
    lyrics = extract_lyrics(response)
    return jsonify({'lyrics': lyrics})


@app.route('/generate-lyrics-artist', methods=['POST'])
def generate_lyrics_artist():
    prompt = request.json.get('prompt')
    artist = request.json.get('artist')
    language = request.json.get('language')
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user",
             "content": f"generate a lyrics that have song topic is {prompt} in {language} language and and in the style of {artist} artist. (just give me only lyrics)"}
        ]
    )
    response = completion.choices[0].message.content
    lyrics = extract_lyrics(response)
    return jsonify({'lyrics': lyrics})


previous_response = ""


@app.route('/ai-assistance', methods=['POST'])
def ai_assistance():
    global previous_response
    prompt = request.json.get('prompt')

    if not previous_response:
        music_info_prompt = f"Extract musical information from the given lyrics and give me Chord,Keys,Time signature and tempo that suit this lyrics:\nUser: {prompt}\n"
    else:
        music_info_prompt = f"User: {previous_response}\nAI: {prompt}"

    # Generate a response using OpenAI GPT-3.5
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": music_info_prompt}
        ]
    )

    response = completion.choices[0].message.content.strip()

    previous_response = response

    return jsonify({'response': response})



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
