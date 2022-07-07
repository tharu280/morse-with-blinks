import cv2
import mediapipe as mp
import pyttsx3
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.config import Config
Config.set('graphics', 'width', '430')
Config.set('graphics', 'height', '780')
Config.write()
Window.clearcolor = (197, 206, 206, 0.5)


class MorseApp(App):

    def build(self):
        self.btncounter=0
        self.ear1previous = []
        self.ear2previous = []
        self.wArray = []
        self.Long = False
        self.Blinked = False
        self.notBlnkdFor = 0
        self.blnkdFor = 0
        self.ltrArray = ""
        self.ltrIs = ""
        self.MCLibrary = {
            "FS": "A",
            "SFFF": "B",
            "SFSF": "C",
            "SFF": "D",
            "F": "E",
            "FFSF": "F",
            "SSF": "G",
            "FFFF": "H",
            "FF": "I",
            "FSSS": "J",
            "SFS": "K",
            "FSFF": "L",
            "SS": "M",
            "SF": "N",
            "SSS": "O",
            "FSSF": "P",
            "SSFS": "Q",
            "FSF": "R",
            "FFF": "S",
            "S": "T",
            "FFS": "U",
            "FFFS": "V",
            "FSS": "W",
            "SFFS": "X",
            "SFSS": "Y",
            "SSFF": "Z"
        }
        self.previousTime = 0
        self.mpDraw = mp.solutions.drawing_utils
        self.mpFmesh = mp.solutions.face_mesh
        self.fmesh = self.mpFmesh.FaceMesh(max_num_faces=1)
        self.drawSpec = self.mpDraw.DrawingSpec(thickness=1, circle_radius=2)
        self.runit = True
        self.img1 = Image(size_hint=(.98, .8), pos_hint={'x': .01, 'y': 0})
        self.img2 = Image(source="MorseImg.png",size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        self.lbl = Label(size_hint=(.98, .06), bold=True, color=(0, 0, 77, 1), pos_hint={'x': .01, 'y': 0}, font_size=60)
        self.lbl.text = " "
        self.button1 = Button( size_hint=(.75, .075), bold=True,  color=(1, 1, 1, 1), pos_hint={'x': .13, 'y': .04},
                               font_size=50)
        self.button1.text = "Start"
        self.button1.bind(on_press=self.callback)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.img1)
        layout.add_widget(self.lbl)
        layout.add_widget(self.button1)
        layout.add_widget(self.img2)


        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 33.0)

        return layout

    def update(self, *args):
        if self.runit:
            ret, frame = self.capture.read()
            buf = cv2.flip(frame, 0).tobytes()
            img_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img1.texture = img_texture

        else:
            ret, frame = self.capture.read()
            imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            meshResult = self.fmesh.process(imgRGB)
            currentTime = time.time()
            fps = 1 / (currentTime - self.previousTime)
            self.previousTime = currentTime
            counter = 0
            if meshResult.multi_face_landmarks:
                for faceLm in meshResult.multi_face_landmarks:
                    self.mpDraw.draw_landmarks(frame, faceLm, self.mpFmesh.FACEMESH_CONTOURS, self.drawSpec,
                                               self.drawSpec)

                    eyeR1v = abs((faceLm.landmark[160].x - faceLm.landmark[144].x) ** 2 - (
                            faceLm.landmark[160].y - faceLm.landmark[144].y) ** 2) + abs(
                        (faceLm.landmark[158].x - faceLm.landmark[153].x) ** 2 - (
                                faceLm.landmark[158].y - faceLm.landmark[153].y) ** 2) / abs(
                        ((faceLm.landmark[33].x - faceLm.landmark[133].x) ** 2) - (
                                (faceLm.landmark[33].y - faceLm.landmark[133].y) ** 2))
                    eyeR2v = abs((faceLm.landmark[385].x - faceLm.landmark[380].x) ** 2 - (
                            faceLm.landmark[385].y - faceLm.landmark[380].y) ** 2) + abs(
                        (faceLm.landmark[387].x - faceLm.landmark[373].x) ** 2 - (
                                faceLm.landmark[387].y - faceLm.landmark[373].y) ** 2) / abs(
                        ((faceLm.landmark[362].x - faceLm.landmark[263].x) ** 2) - (
                                (faceLm.landmark[362].y - faceLm.landmark[263].y) ** 2))

                    if counter > 10:
                        counter = 0
                    else:
                        counter = counter + 1

                    if len(self.ear1previous) > 10:
                        self.ear1previous[counter] = eyeR1v
                        self.Long = True
                    else:
                        self.ear1previous.append(eyeR1v)

                    if len(self.ear2previous) > 10:
                        self.ear2previous[counter] = eyeR2v
                        self.Long = True
                    else:
                        self.ear2previous.append(eyeR2v)

                    if self.Long:
                        if (self.ear1previous[abs(counter - 9)] * 0.70 > eyeR1v) and (
                                self.ear2previous[abs(counter - 9)] * 0.70 > eyeR2v):
                            self.Blinked = True
                            self.blnkdFor = self.blnkdFor + 1
                        else:
                            if self.blnkdFor > (fps * .8):
                                self.ltrArray = self.ltrArray + "S"
                                self.blnkdFor = 0

                            elif self.blnkdFor > int(fps / 8):
                                self.ltrArray = self.ltrArray + "F"
                                self.blnkdFor = 0
                                
                            else:

                                self.notBlnkdFor = self.notBlnkdFor + 1
                                if self.notBlnkdFor > fps * 2:
                                    print(self.ltrArray)
                                    if self.ltrArray in self.MCLibrary:
                                        self.ltrIs = self.MCLibrary[self.ltrArray]
                                        self.wArray.append(self.ltrIs)
                                        self.ltrArray = ""
                                    self.ltrArray = ""
                                    self.notBlnkdFor = 0

            self.finalLetters = " ".join(self.wArray)
            self.lbl.text = self.finalLetters
            buf = cv2.flip(frame, 0).tobytes()
            img_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img1.texture = img_texture

    def callback(self, *args):
        self.btncounter = self.btncounter + 1
        if (self.btncounter % 2) == 0:
            self.runit = True
            self.button1.text = "Start"
        else:
            self.runit = False
            self.button1.text = "Stop"


if __name__ == '__main__':
    MorseApp().run()
