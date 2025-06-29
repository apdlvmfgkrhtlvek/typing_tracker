from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtCore import pyqtSignal
from pynput import keyboard
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QSize
import sys
import time
import math

# TODO
# gif 변경 gui만들기 
# txt파일에 통계 배열 저장하기 
# 통계 보는 gui만들기  
# 단축키 설정해서 위치 옮길 수 있게만들기 
# 코드 최적화 
# 할 수 있으면 매크로 기능 + 매크로 gui까지 

class WPMTracker(QtWidgets.QWidget):
    toggle_timer = pyqtSignal(bool)


    def __init__(self):
        super().__init__()
        self.total_typed = 0
        self.best_wpm = 0
        self.total_time = 0

        self.total_key_typed_arr = [0] * 40

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

        self.timer2 = QtCore.QTimer()
        self.timer2.timeout.connect(self.update_timer)  # 타이핑 시간 재기용
        self.toggle_timer.connect(self.handle_timer)
        self.timer2.start(1000) 
        
    def init_ui(self):
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        gif_width = 220
        gif_height = 147
        margin_x = 20
        margin_y = 20

        # 윈도우 위치를 왼쪽 아래에 붙임
        window_x = margin_x
        window_y = screen_height - gif_height - margin_y
        window_width = gif_width + 150  # 텍스트 라벨 포함해서 너비 좀 넓게
        window_height = gif_height

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(window_x, window_y, window_width, window_height)

        # 텍스트 라벨
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(gif_width, 0, 150, gif_height)  # gif 오른쪽에 붙이임
        self.label.setStyleSheet("color: white; font-size: 20px; font-weight:bold; background-color: rgba(0,0,0,0);")
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(1, 1)
        shadow.setColor(QtGui.QColor(0, 0, 0))
        self.label.setGraphicsEffect(shadow)

        # gif 라벨
        self.gif_label = QtWidgets.QLabel(self)
        self.gif_label.setGeometry(0, 0, gif_width, gif_height)

        self.movie = QMovie("gif/keyboard-type-cat.gif")
        self.gif_label.setMovie(self.movie)
        self.movie.setScaledSize(QSize(gif_width, gif_height))
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
            
            
            ch = key.char
            

            if not ch.isalnum():
                pass

            if ch.isalpha():       
                self.idx = ord(ch.lower()) - ord('a')
                self.total_key_typed_arr[self.idx] += 1

            elif ch.isdigit():
                self.idx = 26 + (ord(ch) - ord('0'))
                self.total_key_typed_arr[self.idx] += 1
           

        except AttributeError:
            pass

    def on_release(self, key): # 임마는 때질때 코드 
        # try:
        #     if hasattr(key, 'char') and key.char:
        #         self.pressed_keys.add(key.char.lower())
        # except:
        #     print(key)
        #     if key == keyboard.Key.esc:
        #         self.pressed_keys.add('esc')

        # if 'esc' in self.pressed_keys and 'q' in self.pressed_keys:
        #     print(self.pressed_keys)
        #     QtWidgets.QApplication.quit()

        try:
            if key.char:
                self.pressed_keys.add(key.char.lower())
        except AttributeError:
            if key == keyboard.Key.esc:
                self.pressed_keys.add('esc')

        if 'esc' in self.pressed_keys and 'q' in self.pressed_keys:
            print(self.total_key_typed_arr)
            QtWidgets.QApplication.quit()   


    def update_timer(self):
        self.total_time += 1

    def handle_timer(self,is_start):
        if is_start:
            if not self.timer2.isActive():
                self.timer2.start()
        else:
            if self.timer2.isActive():
                self.timer2.stop()


    def check_typing(self):
        current_time = time.time()
        time_df = current_time - self.start

        if current_time - self.last_key_typed > 5: # 입력 안할때 그냥 wpm 측정안하기
            self.start = current_time
            self.typed = 0
            self.movie.setSpeed(0)
            self.toggle_timer.emit(False)

        else:
            self.toggle_timer.emit(True)
        

        a = self.typed / 5
        b = time_df / 60
        base_wpm = a/b

        if time_df < 5 and self.typed < 10: # 입력 초반에 wpm 뻥튀기 막기
            wpm = 0           
        else:
            wpm = math.trunc(base_wpm)

        if(wpm < 10):
            self.movie.stop()
        elif(wpm<30):
            self.movie.start()
            self.movie.setSpeed(100)
        elif(wpm<60):
            self.movie.start()
            self.movie.setSpeed(200)
        elif(wpm<100):
            self.movie.setSpeed(400)
        elif(wpm>100):
            self.movie.start()
            self.movie.setSpeed(800)


        if wpm > self.best_wpm: 
            self.best_wpm = wpm

        self.label.setText(
            f"{wpm} wpm\n"
            f"{self.best_wpm} Bwpm\n"
            f"{self.total_typed} TOTAL\n"
            f"{self.total_time}Second"
        )
         


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = WPMTracker()
    win.show()
    sys.exit(app.exec_())
