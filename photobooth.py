#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import PIL
from PIL import Image, ImageTk
import time
import tkinter
from camera import Camera
from qr_generator import QRGenerator
import subprocess
import uuid

try:
    import picamera

    MOCK_MODE = False
except:
    MOCK_MODE = True  # Activate this to test the stand without the camera


class PhotoBooth:
    def __init__(self, window, window_title, camera):
        self.window = self.full_screen_window(window, window_title)
        self.cam = camera
        self.delay = 1
        self.countdown = 0
        self.qr_gen = QRGenerator()
        self.qr_img = None
        self.border_image = Image.open("img/marco_jazmin_1296-972.png")
        self.border_image_HQ = Image.open("img/marco_jazmin_2592-1944.png")

        # Create a canvas that can fit the above video source size
        print("Creating canvas with size {}x{}".format(window.winfo_screenwidth(), window.winfo_screenheight()))
        self.canvas = tkinter.Canvas(window, width=window.winfo_screenwidth(), height=window.winfo_screenheight())
        self.canvas.pack(anchor='center')

        # bind the keys
        self.window.bind('<Return>', self.start_snapshot)
        self.window.bind('<KP_Enter>', self.start_snapshot)
        self.window.bind('1', self.accept_photo)
        self.window.bind('<KP_1>', self.accept_photo)
        self.window.bind('0', self.reject_photo)
        self.window.bind('<KP_0>', self.reject_photo)
        self.window.bind('5', self.reset)
        self.window.bind('<KP_5>', self.reset)

        # TODO: Bind the raspberry buttons

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.is_recording = True
        self.is_saving = False
        self.frame = self.cam.capture(None, True)
        # self.frame = self.frame.resize((800, 600))
        self.photo = PIL.ImageTk.PhotoImage(self.frame)
        print(window.winfo_screenwidth(), window.winfo_screenheight())
        self.photo_on_canvas = self.canvas.create_image(window.winfo_screenwidth() / 2, window.winfo_screenheight() / 2,
                                                        image=self.photo, anchor=tkinter.CENTER)
        self.message_on_canvas = None
        self.message_on_canvas_rectangle = None
        self.message_on_canvas_top = None
        self.message_on_canvas_top_rectangle = None
        self.countdown_on_canvas = None
        self.countdown_on_canvas_rectangle = None
        self.qr_on_canvas = None

        self.update()
        self.window.mainloop()

    def full_screen_window(self, window, window_title):
        window.title(window_title)
        # window.overrideredirect(True)
        window.geometry("{0}x{1}+0+0".format(window.winfo_screenwidth(), window.winfo_screenheight()))
        window.focus_set()
        # ugly hack to prevent the full screen to mess with the keybindings...
        window.attributes("-zoomed", True)
        window.overrideredirect(True)
        window.overrideredirect(False)
        window.attributes('-fullscreen', True)
        # bind Escape key to quit
        window.bind("<Escape>", lambda e: window.destroy())
        return window

    def update(self):
        if self.is_recording:
            print("capturing frame...")
            self.frame = self.cam.capture(None, True)
            # self.frame.paste(self.border_image, (0, 0), self.border_image)
            # self.frame = self.frame.resize((800, 600))
            self.photo = PIL.ImageTk.PhotoImage(self.frame)
            self.canvas.itemconfig(self.photo_on_canvas, image=self.photo)

        self.window.after(self.delay, self.update)

    def start_snapshot(self, event):
        if self.is_recording:
            if self.countdown > 0:
                return
            self.countdown_on_canvas = self.canvas.create_text(self.canvas.winfo_width() / 2,
                                                               self.canvas.winfo_height() - 80,
                                                               justify=tkinter.CENTER, font=("Roboto", 50, "bold"),
                                                               text="Sacando foto en %s...\n¡No se muevan!" % self.countdown)
            self.countdown_on_canvas_rectangle = self.canvas.create_rectangle(
                self.canvas.bbox(self.countdown_on_canvas),
                outline="black", fill="white")
            self.canvas.tag_raise(self.countdown_on_canvas, self.countdown_on_canvas_rectangle)
            self.snapshot_countdown(5)

    def snapshot_countdown(self, count=None):
        if count != None or self.countdown > 1:
            self.countdown = count if count != None else self.countdown - 1
            print("Counting %s..." % self.countdown)
            self.canvas.itemconfig(self.countdown_on_canvas,
                                   text="Sacando foto en %s...\n¡No te muevas!" % self.countdown)
            self.window.after(1000, self.snapshot_countdown)
        else:
            self.countdown -= 1
            if self.countdown_on_canvas != None:
                self.canvas.delete(self.countdown_on_canvas)
            if self.countdown_on_canvas_rectangle != None:
                self.canvas.delete(self.countdown_on_canvas_rectangle)
            self.snapshot()

    def snapshot(self):
        print("Saving snapshot...")
        self.is_recording = False
        self.is_saving = True
        self.frame = self.cam.captureHQ(None, False)
        self.frame.paste(self.border_image_HQ, (0, 0), self.border_image_HQ)
        self.photo = PIL.ImageTk.PhotoImage(
            self.frame.resize((self.window.winfo_screenwidth(), self.window.winfo_screenheight())))
        self.canvas.itemconfig(self.photo_on_canvas, image=self.photo)
        self.message_on_canvas = self.canvas.create_text(self.canvas.winfo_width() / 2,
                                                         self.canvas.winfo_height() - 120,
                                                         # fill="darkblue",
                                                         justify=tkinter.CENTER, font=("Roboto", 50, "bold"),
                                                         text="¿Querés guardar la foto?\n 1=SI, 0=NO")
        self.message_on_canvas_rectangle = self.canvas.create_rectangle(self.canvas.bbox(self.message_on_canvas),
                                                                        outline="black", fill="white")
        self.canvas.tag_raise(self.message_on_canvas, self.message_on_canvas_rectangle)
        self.output_file = "snapshots/%s.jpg" % time.strftime("%Y%m%d-%H%M%S")
        self.frame.save(self.output_file)
        print("Snapshot saved in %s" % self.output_file)

    def accept_photo(self, event):
        if self.is_recording:
            return
        if not self.is_saving:
            return
        print("Photo accepted.")
        self.canvas.itemconfig(self.message_on_canvas, text="Guardando foto...")
        accepted_output_file = uuid.uuid5(uuid.NAMESPACE_DNS, self.output_file)
        accepted_output_path = "accepted_photos/%s.jpg" % accepted_output_file
        server_location = "someuser@my.server.com:/path/to/www/photos"
        try:
            print("rsync -az '%s' '%s'" % (self.output_file, accepted_output_path))
            ret1 = subprocess.call(["rsync", "-az", self.output_file, accepted_output_path])
            print("rsync -az '%s' '%s'" % (accepted_output_path, server_location))
            ret2 = subprocess.call(["rsync", "-az", accepted_output_path, server_location])
            if ret1!=0 or ret2!=0:
                raise
        except:
            self.upload_failed()
            return
        self.qr_img = PIL.ImageTk.PhotoImage(self.qr_gen.generate_url(accepted_output_file))
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.qr_on_canvas = self.canvas.create_image(width / 2, height / 2, anchor=tkinter.CENTER, image=self.qr_img)
        self.message_on_canvas_top = self.canvas.create_text(self.canvas.winfo_width() / 2, 120,
                                                             # fill="darkblue",
                                                             justify=tkinter.CENTER, font=("Roboto", 50, "bold"),
                                                             text="¡La imagen fue guardada!")
        self.message_on_canvas_top_rectangle = self.canvas.create_rectangle(
            self.canvas.bbox(self.message_on_canvas_top),
            outline="black", fill="white")
        self.canvas.tag_raise(self.message_on_canvas_top, self.message_on_canvas_top_rectangle)
        self.canvas.itemconfig(self.message_on_canvas,
                               text="Podés escanear el código QR para verla.\nPresioná 5 para volver a empezar :)")
        if self.message_on_canvas_rectangle != None:
            self.canvas.delete(self.message_on_canvas_rectangle)
        self.message_on_canvas_rectangle = self.canvas.create_rectangle(self.canvas.bbox(self.message_on_canvas),
                                                                        outline="black", fill="white")
        self.canvas.tag_raise(self.message_on_canvas, self.message_on_canvas_rectangle)

    def upload_failed(self):
        print("Upload failed")
        self.canvas.itemconfig(self.message_on_canvas,
                               text="¡Oh, no! La foto no se ha podido subir\n¡Avisale a los organizadores! :(")
        if self.message_on_canvas_rectangle != None:
            self.canvas.delete(self.message_on_canvas_rectangle)
        self.message_on_canvas_rectangle = self.canvas.create_rectangle(self.canvas.bbox(self.message_on_canvas),
                                                                        outline="black", fill="white")
        self.canvas.tag_raise(self.message_on_canvas, self.message_on_canvas_rectangle)
        self.window.after(5000, self.resume)

    def reject_photo(self, event):
        if self.is_recording:
            return
        print("Photo rejected")
        self.resume()

    def reset(self, event):
        if not self.is_saving:
            return
        self.resume()

    def resume(self):
        if self.message_on_canvas != None:
            self.canvas.delete(self.message_on_canvas)
        if self.message_on_canvas_rectangle != None:
            self.canvas.delete(self.message_on_canvas_rectangle)
        if self.message_on_canvas_top != None:
            self.canvas.delete(self.message_on_canvas_top)
        if self.message_on_canvas_top_rectangle != None:
            self.canvas.delete(self.message_on_canvas_top_rectangle)
        if self.countdown_on_canvas != None:
            self.canvas.delete(self.countdown_on_canvas)
        if self.countdown_on_canvas_rectangle != None:
            self.canvas.delete(self.countdown_on_canvas_rectangle)
        if self.qr_on_canvas != None:
            self.canvas.delete(self.qr_on_canvas)
        self.countdown = 0
        self.is_recording = True
        self.is_saving = False


def main():
    """
    Main program loop
    """

    # Create the window object
    tk = tkinter.Tk()

    # Create the camera object
    cam = Camera(MOCK_MODE, tk)

    # Create a window and pass it to the Application object
    PhotoBooth(tk, "PhotoBooth", cam)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("keyboard interrupt")
    except Exception as exception:
        raise
