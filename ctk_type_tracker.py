from pynput import keyboard
import time
import math
import customtkinter as ctk
import requests

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("200x150+0+1470")
app.wm_attributes("-transparentcolor", "gray20")

app.attributes('-alpha', 0.9) # 글자 투명도 설정

app.configure(bg="gray20")
app.wm_attributes("-topmost", True)
app.overrideredirect(True)
app.title("KeyTracker")

frame = ctk.CTkFrame(master=app, fg_color="gray20")  
frame.pack(pady=0, padx=0, fill="both", expand=True)

label = ctk.CTkLabel(master=frame, text="wpm : \n 총 글자수 : \n 타이핑 시간 : ", text_color="white", font=("Roboto", 20))
label.pack(pady=20)

total_time_start = time.time() # 전체 타이핑 시간
total_typed = 0 # 키보드 누른 횟수
best_wpm = 0 # wpm 최고 기록

typed = 0 # wpm 계산용
last_key_typed = 0 # 키보드 안치는거 인식용

start = time.time() # wpm 계산용
current_time = 0

prev_key = None 

pressed = set()

def on_press(key):# 누를때 인식
    global typed,total_typed,last_key_typed,prev_key,current_time
    try:
        current_time = time.time()
        if (key.char == prev_key and current_time - last_key_typed < 0.2):
            return
        
        prev_key=key.char
        
        total_typed+=1
        typed+=1
        last_key_typed = time.time()

        data = {
            "username": "test", 
            "key": key.char,
            "typed": total_typed, 
            "timestamp": current_time
        }

        # response = requests.post("http://localhost:3000/api/keyboard/typed", json=data)

    except AttributeError:
        return
    

def on_release(key): # 키보드에서 손 땔때 인식
    try:
        if key.char:
            pressed.add(key.char.lower())
    except AttributeError:
        if key == keyboard.Key.esc:
            pressed.add('esc')

    if 'esc' in pressed and 'q' in pressed:
        app.destroy()



def check_typing():
    global start,typed,total_typed,total_time_start,best_wpm

    current_time = time.time()
    time_df = current_time - start
    
    if current_time - last_key_typed > 7:
        start=time.time()
        typed=0

    if time_df<2:
        wpm=0
    else:
        a=typed/5   
        b=time_df/60    
        wpm=math.trunc(a/b)

    if wpm > best_wpm:
        best_wpm = wpm

    total_time = math.trunc(current_time - total_time_start)

    label.configure(text=f"wpm : {wpm} \n best wpm : {best_wpm} \n 총 글자수 : {total_typed} \n 타이핑 시간 : {math.trunc(total_time)}초 ") 
    app.after(100, check_typing)

check_typing()


listener = keyboard.Listener(on_press=on_press,on_release=on_release)
listener.start()

app.mainloop()