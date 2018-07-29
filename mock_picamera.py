#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
import random
import cv2


class PiCamera:
    def __init__(self):
        self.im = Image.open("img/placeholder.jpg")
        self.imcv2 = cv2.imread("img/placeholder.jpg")

    def capture(self, img, format, resize, use_video_port):
        image = cv2.resize(self.imcv2, self.resolution)
        noise_img = self.sp_noise(image, 0.2)
        im = Image.fromarray(noise_img)
        im.save(img, format)
        return

    def sp_noise(self, image, prob):
        '''
        Add salt and pepper noise to image
        prob: Probability of the noise
        '''
        # output = np.zeros(image.shape, np.uint8)
        output = np.copy(image)
        for i in range(0, image.shape[0], 5):
            for j in range(0, image.shape[1], 5):
                if True:
                    output[i][j] = random.randint(0, 255)
        return output
