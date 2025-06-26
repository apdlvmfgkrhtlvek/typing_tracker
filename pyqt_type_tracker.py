from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from pynput import keyboard
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QSize
import sys
import time
import math

class WPMTracker(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.total_time_start = time.time()
        self.total_typed = 0
        self.best_wpm = 0

        self.typed = 0
        self.last_key_typed = 0
        self.start = time.time()
        self.prev_key = None
        self.pressed_keys = set()

        self.init_ui()

        self.timer = QtCore.QTimer() # 0.1초 마다 check_typing 함수 호출
        self.timer.timeout.connect(self.check_typing)
        self.timer.start(100)

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def init_ui(self): # ui 생성
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(-150, 1130, 600, 1000)# tq 해상도 맞춰서 움직이게 설정해야됨 지금은 1920 x 1200기준

        self.label = QtWidgets.QLabel(self)
        self.label.setStyleSheet("color: white; font-size: 30px; font-weight:bold; background-color: rgba(0,0,0,0);")
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(1, 1)
        shadow.setColor(QtGui.QColor(0, 0, 0))  # 검정색 그림자
        
        self.label.setGraphicsEffect(shadow)

        
        self.gif_label = QtWidgets.QLabel(self) #gif랑 텍스트랑 위치 따로 배치하기위해서 따로 라벨생성
        self.gif_label.setGeometry(200, 250, 220, 147)

        self.movie = QMovie("pusheen-fast-unscreen.gif")
        self.gif_label.setMovie(self.movie)
        self.movie.setScaledSize(QSize(220,147))
        self.movie.start()


    def on_press(self, key): # 눌릴때 코드
        try:
            current_time = time.time()
            if key.char == self.prev_key and current_time - self.last_key_typed < 0.2:
                return

            self.prev_key = key.char
            self.total_typed += 1
            self.typed += 1
            self.last_key_typed = current_time

            # 백엔드 전송용
            # data = {
            #     "username": "test",
            #     "key": key.char,
            #     "typed": self.total_typed,
            #     "timestamp": current_time
            # }

        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                self.pressed_keys.add(key.char.lower())
        except:
            print(key)
            if key == keyboard.Key.esc:
                self.pressed_keys.add('esc')

        if 'esc' in self.pressed_keys and 'q' in self.pressed_keys:
            print(self.pressed_keys)
            QtWidgets.QApplication.quit()

    def check_typing(self):
        current_time = time.time()
        time_df = current_time - self.start

        if current_time - self.last_key_typed > 10: # 입력 안할때 그냥 wpm 측정안하기
            self.start = current_time
            self.typed = 0
            self.movie.setSpeed(0)


        if time_df < 2: # 입력 초반에 wpm 뻥튀기 막기
            wpm = 0
        else:
            a = self.typed / 5
            b = time_df / 60
            wpm = math.trunc(a / b)
        if(wpm < 10):
            self.movie.stop()
        elif(wpm<30):
            self.movie.start()
            self.movie.setSpeed(100)
        elif(wpm<60):
            self.movie.start()
            self.movie.setSpeed(200)
        elif(wpm>100):
            self.movie.start()
            self.movie.setSpeed(800)


        if wpm > self.best_wpm: 
            self.best_wpm = wpm

        total_time = math.trunc(current_time - self.total_time_start)

        self.label.setText(
            f"wpm : {wpm}\n"
            f"best wpm : {self.best_wpm}\n"
            f"총 글자수 : {self.total_typed}\n"
            f"타이핑 시간 : {total_time}초"
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = WPMTracker()
    win.show()
    sys.exit(app.exec_())
