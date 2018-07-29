#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from io import BytesIO
from PIL import Image

try:
    import picamera
except:
    import mock_picamera
    import cv2_picamera

    sys.modules['picamera'] = mock_picamera
    # sys.modules['picamera'] = cv2_picamera
    import picamera


class Camera:
    def __init__(self, mock_mode, window):
        self.stream = BytesIO()
        self.im = None
        self.camera = self.init_camera(mock_mode, window)
        self.width = self.camera.resolution[0]
        self.height = self.camera.resolution[1]
        self.photo = self.capture()

    def init_camera(self, mock_mode, window):
        window_width, window_height = window.winfo_screenwidth(), window.winfo_screenheight()
        photo_w = min(1920, window_width)
        photo_h = min(1080, window_height)
        # Try to initialize the camera
        try:
            camera = picamera.PiCamera() if not mock_mode else mock_picamera.PiCamera()
        except:
            print("error initializing the camera - exiting")
            raise
        # Configure the camera
        camera.hflip = True
        camera.rotation = 0
        camera.annotate_text_size = 80
        camera.resolution = (1296, 972)
        camera.framerate = 42
        # camera.shutter_speed = 800
        return camera

    def capture(self, resize=None, video_port=True):
        self.stream.seek(0)
        self.camera.capture(self.stream, format='jpeg', resize=resize, use_video_port=video_port)
        self.stream.truncate()
        self.stream.seek(0)
        self.im = Image.open(self.stream)
        return self.im

    def captureHQ(self, resize=None, video_port=False):
        resolution = self.camera.resolution
        framerate = self.camera.framerate
        self.camera.resolution = (2592, 1944)
        self.camera.framerate = 15
        self.camera.hflip = False
        self.stream.seek(0)
        self.camera.capture(self.stream, format='jpeg', resize=resize, use_video_port=video_port)
        self.stream.truncate()
        self.stream.seek(0)
        self.im = Image.open(self.stream)
        self.camera.hflip = True
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        return self.im
