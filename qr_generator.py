#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import qrcode


class QRGenerator:
    def generate_url(self, filename):
        print("Generating QR for %s" % filename)
        url = "https://photos.server.com/{}.jpg".format(filename)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4, )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img
