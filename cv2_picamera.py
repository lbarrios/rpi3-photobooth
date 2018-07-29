#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
from PIL import Image


class PiCamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        # Check if the webcam is opened correctly
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")
        ret, self.frame = self.cap.read()
        # self.frame = cv2.resize(self.frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        self.im = Image.fromarray(self.frame)
        self.imcv2 = self.frame

    def capture(self, img, format, resize, use_video_port):
        ret, self.frame = self.cap.read()
        # self.frame = cv2.resize(self.frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        im = Image.fromarray(self.frame)
        im.save(img, format)
        return

    def sp_noise(self, image, prob):
        '''
        Add salt and pepper noise to image
        prob: Probability of the noise
        '''
        # output = np.zeros(image.shape, np.uint8)
        output = np.copy(image)
        for i in range(0, image.shape[0], 1):
            for j in range(0, image.shape[1], 1):
                if random.random() < prob:
                    output[i][j] = random.randint(0, 255)
        return output