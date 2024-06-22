# services/camera_service.py

from service.camera import VideoCamera

emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
df1 = None
emotion = None


class CameraService:
    def __init__(self):
        self.camera = VideoCamera()

    def gen(self):
        global df1, emotion
        while True:
            frame, df1, emotion = self.camera.get_frame()
            print(f"Emotion: {emotion}")
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def get_music_recommendations(self):
        global df1, emotion
        if df1 is not None and not df1.empty:

            response = {
                "songs": df1.to_json(orient='records'),
                "emotion": emotion
            }
            return response
        elif emotion == "Unknown":
            return {"error": "Mood could not be detected, Try again", "songs": [], "emotion": None}
        else:
            return {"error": "No face detected", "songs": [], "emotion": None}
