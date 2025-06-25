from pynput import keyboard
import time
import math
import customtkinter as ctk

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("200x150+0+1520")
app.wm_attributes("-transparentcolor", "gray20")
app.attributes('-alpha', 0.5)
app.configure(bg="gray20")
app.wm_attributes("-topmost", True)
app.overrideredirect(True)
app.title("KeyTracker")

frame = ctk.CTkFrame(master=app, fg_color="gray20")  
frame.pack(pady=0, padx=0, fill="both", expand=True)

label = ctk.CTkLabel(master=frame, text="wpm : \n 총 글자수 : \n 타이핑 시간 : ", text_color="white", font=("Roboto", 20))
label.pack(pady=20)


start = time.time()
total_time_start = time.time()
total_typed = 0
typed = 0
current_time = 0
last_key_typed = 0
pressed = set()

def on_press(key):
    global typed,total_typed,last_key_typed
    total_typed+=1
    typed+=1
    last_key_typed = time.time()
    

def on_release(key):
    try:
        if key.char:
            pressed.add(key.char.lower())
    except AttributeError:
        if key == keyboard.Key.esc:
            pressed.add('esc')

    if 'esc' in pressed and 'q' in pressed:
        app.destroy()



def check_typing():
    global start,typed,total_typed,total_time_start

    current_time = time.time()
    time_df = current_time - start

    if(current_time - last_key_typed > 5):
        start=time.time()
        typed=0

    a=typed/5   
    b=time_df/60    
    wpm=math.trunc(a/b)

    total_time = math.trunc(current_time - total_time_start)

    label.configure(text=f"wpm : {wpm} \n 총 글자수 : {total_typed} \n 타이핑 시간 : {total_time}초") 
    app.after(100, check_typing)

check_typing()


listener = keyboard.Listener(on_press=on_press,on_release=on_release)
listener.start()

app.mainloop()