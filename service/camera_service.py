# camera_service.py
from model.camera import VideoCamera

emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
df1 = None
emotion = None

def gen(camera):
    global df1, emotion
    while True:
        frame, df1, emotion = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def get_music_recommendations():
    global df1, emotion
    if df1 is not None:
        response = {
            "songs": df1.to_json(orient='records'),
            "emotion": emotion
        }
        return response
    else:
        return {"songs": [], "emotion": None}
