# camera_controller.py

from flask import Response, jsonify
from model.camera import VideoCamera
from service.camera_service import gen, get_music_recommendations

def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_table():
    response = get_music_recommendations()
    return jsonify(response)
