import numpy as np
import cv2
from PIL import Image
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
import datetime
from threading import Thread
import pandas as pd
from Database.db_connection import create_connection, close_connection

# Load the face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Load the emotion detection model
emotion_model = Sequential()
emotion_model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 1)))
emotion_model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Dropout(0.25))
emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Dropout(0.25))
emotion_model.add(Flatten())
emotion_model.add(Dense(1024, activation='relu'))
emotion_model.add(Dropout(0.5))
emotion_model.add(Dense(7, activation='softmax'))
emotion_model.load_weights('./model/model.h5')

# Define the emotion dictionary
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

# Global variables
global last_frame1
last_frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
global cap1
show_text = [0]

# Class for calculating FPS while streaming
class FPS:
    def __init__(self):
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        self._end = datetime.datetime.now()

    def update(self):
        self._numFrames += 1

    def elapsed(self):
        return (self._end - self._start).total_seconds()

    def fps(self):
        return self._numFrames / self.elapsed()

# Class for using another thread for video streaming
class WebcamVideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

# Class for reading video stream, generating prediction and recommendations
class VideoCamera:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.db_connection = create_connection()

    def __del__(self):
        self.capture.release()
        close_connection(self.db_connection)

    def get_frame(self):
        global df1
        ret, frame = self.capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_rects = face_cascade.detectMultiScale(gray, 1.3, 5)
        df1 = self.fetch_music_recommendations(show_text[0])
        for (x, y, w, h) in face_rects:
            cv2.rectangle(frame, (x, y - 50), (x + w, y + h + 10), (0, 255, 0), 2)
            roi_gray_frame = gray[y:y + h, x:x + w]
            cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)
            prediction = emotion_model.predict(cropped_img)

            maxindex = int(np.argmax(prediction))
            show_text[0] = maxindex
            cv2.putText(frame, emotion_dict[maxindex], (x + 20, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            df1 = self.fetch_music_recommendations(show_text[0])

        global last_frame1
        last_frame1 = frame.copy()
        pic = cv2.cvtColor(last_frame1, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(last_frame1)
        img = np.array(img)
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes(), df1, emotion_dict[show_text[0]]

    def fetch_music_recommendations(self, emotion_index):
        cursor = self.db_connection.cursor(dictionary=True)
        query = "SELECT Name, Album, Artist, Image, Spotify_link FROM spotify_track WHERE emotion = %s ORDER BY RAND() LIMIT 15"
        cursor.execute(query, (emotion_dict[emotion_index],))
        result = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(result)

