import time
import tkinter as tk
import matplotlib.ticker as ticker
from tkinter import ttk, PhotoImage
from tkinter import messagebox
from tkinter import scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import math
import subprocess
import serial
import serial.tools.list_ports
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import sys
import binascii
import base64

senserR1=[100,100,100,100,100,100,100,100,100,100,100,100,100,100,-90,90,180,0,-1]#Tof左,前,右,後,Line左前,右前,右後,左後,Moter左前,右前,右後,左後,機体角度,進行方向
senserR2=[100,100,100,100,100,100,100,100,100,100,100,100,100,100,90,90,9-130,0,-1]#Tof左,前,右,後,Line左前,右前,右後,左後,Moter左前,右前,右後,左後,機体角度,進行方向
serialPort = None
lineSeting = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
lineBorder = 10
nowlineBorder = "None"
cameraLIDAR = [200,40,110,150,150,0,0,0,0,0,0,0,0,0,0,0]
mypositionVal = [0,0,0,0]
#ser = None
mainStop=False
message="ad64b3f4670838df6c13b98ad4b037e78bafa2619d6e34d23018c9fbcef48d9282c134ffbb029fbe9c54e8d7e97138fa"
urtext = ""
urlogTxt = []
WDSSerialMode = 0
PORT_FILE_PATH = 'WDSfile/last_port.txt'

yellowGoalCanvas1 = None
yellowGoalCanvas2 = None
blueGoalCanvas1 = None
blueGoalCanvas2 = None
ballCanvas1 = None
ballCanvas2 = None
goRadCanvas1 = None
goRadCanvas2 = None



#key = os.urandom(16)
"""
key = bytes.fromhex("e79a7c657467cf0797d86f0a0dec6818")
iv = os.urandom(16)
data = b"Ro/soud/"
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
encryptor = cipher.encryptor()
pad_length = 16 - (len(data) % 16)
padded_data = data + bytes([pad_length]) * pad_length
ciphertext = encryptor.update(padded_data) + encryptor.finalize()
print(key.hex())
print(iv.hex())
print(ciphertext.hex())
"""

def serialSendRead(sendtext):
    if not sendtext == "":
        try:
            with open('WDSfile/command/commandList.txt', 'r', encoding='utf-8') as file:
                list = file.read().split("\n")
            comlist = []
            for i in range(len(list) // 2):
                list[2 * i] = list[2 * i].replace(" > ", "*").replace(" -> ", "*")
                comlist.append(list[2 * i].split("*"))
            sendtextlist = sendtext.split(" > ")
            for i in range(len(comlist)):
                if sendtextlist[1] == comlist[i][0]:
                    if sendtextlist[0] == "R1":
                        with open('WDSfile/key/robo1CommonKey.txt', 'r', encoding='utf-8') as file:
                            keytext = file.read()
                    elif sendtextlist[0] == "R2":
                        with open('WDSfile/key/robo2CommonKey.txt', 'r', encoding='utf-8') as file:
                            keytext = file.read()
                    key = bytes.fromhex(keytext)
                    iv = os.urandom(16)
                    senddata = comlist[i][-1]
                    if len(comlist[i]) >= 3:
                        for i in range(len(comlist[i])-2):
                            senddata = senddata.replace(comlist[i][1+i],sendtextlist[2+i])
                    print(senddata)
                    data = senddata.encode()
                    #data = b"Ro/soud/"
                    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                    encryptor = cipher.encryptor()
                    pad_length = 16 - (len(data) % 16)
                    padded_data = data + bytes([pad_length]) * pad_length
                    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
                    print(key.hex())
                    print(iv.hex())
                    print(ciphertext.hex())
                    ser.write("W".encode())
                    ser.write(iv.hex().encode())
                    ser.write(ciphertext.hex().encode())
        except Exception as e:
            return e

class commandAdd:
    def write(self):
        response = messagebox.askquestion("確認", "本当に保存しますか？")
        if response == 'yes':
            text = self.text_area.get("1.0", tk.END)
            with open('WDSfile/command/commandList.txt', 'w', encoding='utf-8') as file:
                file.write(text)

    def read(self):
        response = messagebox.askquestion("確認", "本当に再読み込みしますか？")
        if response == 'yes':
            self.text_area.delete("1.0", tk.END)
            with open('WDSfile/command/commandList.txt', 'r', encoding='utf-8') as file:
                self.text = file.read()
            self.text_area.insert(tk.END, self.text)

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WDS/コマンド編集")
        self.root.geometry("650x425")
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=30, width=90)
        self.text_area.place(x=0,y=30)
        with open('WDSfile/command/commandList.txt', 'r', encoding='utf-8') as file:
            self.text = file.read()
        self.text_area.insert(tk.END, self.text)
        self.button1 = tk.Button(self.root, text="保存", command=lambda: self.write())
        self.button1.place(x=2,y=2)
        self.button2 = tk.Button(self.root, text="再読み込み", command=lambda: self.read())
        self.button2.place(x=40, y=2)
        self.label1 = tk.Label(self.root,text="書式：[コマンド名] -> [ロボットに送信する電文]　とし、次の行に説明を記入してください")
        self.label1.place(x=120,y=3)
        self.root.mainloop()

class commandlist:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WDS/コマンド一覧")
        self.root.geometry("650x395")
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=30, width=90)
        self.text_area.place(x=0,y=0)
        with open('WDSfile/command/commandList.txt', 'r', encoding='utf-8') as file:
            self.text = file.read()
        self.text_area.insert(tk.END, self.text)
        self.text_area.config(state=tk.DISABLED)
        self.root.mainloop()

class serialMoniter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WDS/シリアルモニター")
        self.root.geometry("650x395")
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=30, width=90, bg="#080613", fg="#FFFFFF", insertbackground='white')
        self.text_area.place(x=0,y=0)
        self.text_area.insert(tk.END, "-----------シリアルモニター-----------\n")
        self.text_area.config(state=tk.DISABLED)
        self.root.mainloop()

    def add_text(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

# シリアルモニターのインスタンスをグローバル変数として保持
serial_monitor_instance = None

class log:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WDS/ログ")
        self.root.geometry("650x395")
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=30, width=90, bg="#080613", fg="#FFFFFF", insertbackground='white')
        self.text_area.place(x=0,y=0)
        self.text_area.insert(tk.END, "-----------ログ-----------")
        self.text_area.config(state=tk.DISABLED)
        self.root.mainloop()

class terminal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WDS/ターミナル")
        self.root.geometry("650x395")
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=30, width=90, bg="#080613", fg="#FFFFFF", insertbackground='white')
        self.text_area.place(x=0,y=0)
        self.text_area.bind("<Return>", self.enterWaite)
        self.text_area.insert(tk.END, "WDS:terminal>")
        self.text_area.mark_set("insert", "end-1c")
        self.text_area.see(tk.END)
        ser.write(f'Se/line/'.encode())
        self.root.mainloop()

    def enterWaite(self, event):
        line_index = self.text_area.index(tk.INSERT).split('.')[0]
        line_text = self.text_area.get(f"{line_index}.0", f"{line_index}.end")
        print(serialSendRead(line_text[13:]))
        print(line_text[13:])
        if self.root.winfo_exists():
            self.root.after(1, self.onEnter)

    def onEnter(self):
        line_index = self.text_area.index(tk.INSERT).split('.')[0]
        self.text_area.mark_set(tk.INSERT, f'{line_index}.end+1c')
        self.text_area.insert(tk.END, 'WDS:terminal>')
        self.text_area.see(tk.INSERT)

class roboInformation:
    def openContent(self, value, content):
        if not self.keyshow[value]:
            content.config(text=f'共通鍵：{self.key[value]}')
            self.keyshow[value] = not self.keyshow[value]
        else:
            content.config(text=f'共通鍵：********************************')
            self.keyshow[value] = not self.keyshow[value]
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WDS/共通鍵登録情報")
        self.root.geometry("330x270")
        self.key = ["","",""]
        try:
            with open('WDSfile/key/robo1CommonKey.txt', 'r', encoding='utf-8') as file:
                self.key[0] = file.read()
            with open('WDSfile/key/robo2CommonKey.txt', 'r', encoding='utf-8') as file:
                self.key[1] = file.read()
            with open('WDSfile/key/roboContactKey.txt', 'r', encoding='utf-8') as file:
                self.key[2] = file.read()
        except Exception as e:
            messagebox.showinfo("警告", "共通鍵を正しく読み込めませんでした")
        self.label1 = tk.Label(self.root, text="ロボット登録情報")
        self.label1.place(x=10, y=10)
        self.label2 = tk.Label(self.root, text="・ロボット1")
        self.label2.place(x=10, y=40)
        self.label3 = tk.Label(self.root, text=f'共通鍵：********************************')
        self.label3.place(x=15, y=60)
        self.label4 = tk.Label(self.root, text="・ロボット2")
        self.label4.place(x=10, y=90)
        self.label5 = tk.Label(self.root, text=f'共通鍵：********************************')
        self.label5.place(x=15, y=110)
        self.label6 = tk.Label(self.root, text="・ロボット間通信")
        self.label6.place(x=10, y=140)
        self.label7 = tk.Label(self.root, text=f'共通鍵：********************************')
        self.label7.place(x=15, y=160)
        self.keyshow = [False, False, False]
        self.checkButton1 = tk.Checkbutton(self.root, text="表示", command=lambda: self.openContent(0, self.label3))
        self.checkButton1.place(x=260, y=60)
        self.checkButton2 = tk.Checkbutton(self.root, text="表示", command=lambda: self.openContent(1, self.label5))
        self.checkButton2.place(x=260, y=110)
        self.checkButton3 = tk.Checkbutton(self.root, text="表示", command=lambda: self.openContent(2, self.label7))
        self.checkButton3.place(x=260, y=160)
        self.root.mainloop()

class addRobot:
    def reset(self):
        self.label1.config(fg="#000000")
        self.pro1.config(fg="#000000", text="▼　新規共通鍵の発行")
        self.pro2.config(fg="#000000", text="▼　共通鍵をパソコンに保存")
        self.pro3.config(fg="#000000", text="▼　ロボットに共通鍵を登録")
        self.pro4.config(fg="#000000", text="▼　ロボットにロボットネームを登録")
        self.pro5.config(fg="#000000", text="▼　完了")

    def makeKey(self):
        stopContent = None
        self.reset()
        if self.roboSelection.get() == "ロボット1" or self.roboSelection.get() == "ロボット2":
            try:
                stopContent = self.pro1
                key = os.urandom(16)
                key_name=[key.hex(), ""]
                self.pro1.config(fg="#009900", text="✔　新規共通鍵の発行")
                keyHex = key.hex()
                stopContent = self.pro2
                with open('WDSfile/key/robo1CommonKey.txt', 'w', encoding='utf-8') as file:
                    file.write(keyHex)
                self.pro2.config(fg="#009900", text="✔　共通鍵をパソコンに保存")
                stopContent = self.pro3
                sendText = f'Ro/dcky/{keyHex}'
                ser.write(sendText.encode())
                time.sleep(0.05)
                self.pro3.config(fg="#009900", text="✔　ロボットに共通鍵を登録")
                stopContent = self.pro4
                if self.roboSelection.get() == "ロボット1":
                    sendText = f'Ro/name/robo1'
                    ser.write(sendText.encode())
                    key_name[1] = "robo1"
                elif self.roboSelection.get() == "ロボット2":
                    sendText = f'Ro/name/robo2'
                    ser.write(sendText.encode())
                    key_name[1] = "robo2"
                self.pro4.config(fg="#009900", text="✔　ロボットにロボットネームを登録")
                self.pro5.config(fg="#009900", text="✔　完了")
            except Exception as e:
                stopContent.config(fg="#FF0000")
        else:
            self.label1.config(fg="#FF0000")

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WDS/共通鍵新規登録")
        self.root.geometry("300x270")
        self.roboSelection = ttk.Combobox(self.root, values=["ロボット1", "ロボット2"])
        self.roboSelection.place(x=10,y=35)
        self.roboSelection.set("選択してください")
        self.label1 = tk.Label(self.root, text = "登録するロボットを選んでください")
        self.label1.place(x=10,y=10)
        self.label2 = tk.Label(self.root, text="ポート設定を行ってから登録してください")
        self.label2.place(x=10, y=60)
        self.label3 = tk.Label(self.root, text="-----------------------------------------------------")
        self.label3.place(x=10, y=80)
        self.pro1 = tk.Label(self.root, text="▼　新規共通鍵の発行")
        self.pro1.place(x=10, y=105)
        self.pro2 = tk.Label(self.root, text="▼　共通鍵をパソコンに保存")
        self.pro2.place(x=10, y=130)
        self.pro3 = tk.Label(self.root, text="▼　ロボットに共通鍵を登録")
        self.pro3.place(x=10, y=155)
        self.pro4 = tk.Label(self.root, text="▼　ロボットにロボットネームを登録")
        self.pro4.place(x=10, y=180)
        self.pro5 = tk.Label(self.root, text="▼　完了")
        self.pro5.place(x=10, y=205)
        self.button1 = tk.Button(self.root, text="登録", command=lambda: self.makeKey())
        self.button1.place(x=170, y=32)
        self.root.mainloop()

class lineSensorPanel:
    def __init__(self, parent):
        global line1_image
        self.root = tk.Toplevel(parent)
        self.root.title("WDS/ラインセンサパネル")
        self.root.geometry("650x275")
        self.label1 = tk.Label(self.root, text="ラインセンサ閾値調整")
        self.label1.place(x=10, y=10)
        self.label2 = tk.Label(self.root, text="閾値モニター")
        self.label2.place(x=300, y=10)
        self.line = tk.Label(self.root, image=line_image)
        self.line.place(x=10, y=45)
        self.button1 = tk.Button(self.root, text="調整", command=lambda: self.lineflf())
        self.button1.place(x=60, y=35)
        self.button2 = tk.Button(self.root, text="調整", command=lambda: self.linefrr())
        self.button2.place(x=190, y=105)
        self.button3 = tk.Button(self.root, text="調整", command=lambda: self.linebll())
        self.button3.place(x=10, y=145)
        self.button4 = tk.Button(self.root, text="調整", command=lambda: self.linebrb())
        self.button4.place(x=110, y=205)
        self.button5 = tk.Button(self.root, text="現在の閾値", command=lambda: self.nowBorder())
        self.button5.place(x=220, y=240)
        self.label3 = tk.Label(self.root, text=nowlineBorder)
        self.label3.place(x=300, y=242)

        # グラフの初期設定
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')  # グラフの線を赤色に設定
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 255)
        
        # グラフのスタイル設定
        self.fig.patch.set_facecolor('#3EB489')  # 背景色を黒に設定
        self.ax.set_facecolor('#3EB489')  # グラフの背景色を黒に設定
        self.ax.tick_params(colors='#7fffbf', direction='in', pad=-15)  # 目盛の色を灰色に設定し、内側に配置
        self.ax.spines['bottom'].set_color('white')  # 下の枠線の色を白に設定
        self.ax.spines['left'].set_color('white')  # 左の枠線の色を白に設定
        self.ax.spines['top'].set_color('white')  # 上の枠線の色を白に設定
        self.ax.spines['right'].set_color('white')  # 右の枠線の色を白に設定
        self.ax.yaxis.label.set_color('white')  # Y軸ラベルの色を白に設定
        self.ax.xaxis.label.set_color('white')  # X軸ラベルの色を白に設定
        self.ax.title.set_color('white')  # タイトルの色を白に設定
        self.ax.yaxis.set_tick_params(direction='in', pad=-30)  # Y軸の数字を内側に配置
        self.ax.xaxis.set_tick_params(direction='in', pad=-15)  # X軸の数字を内側に配置

        self.ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '' if x == 0 or x == 20 else int(x)))
        self.ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: '' if y == 0 else int(y)))

        for y in range(0, 256, 50):
            self.ax.axhline(y=y, color='#7fffbf', linestyle='--', linewidth=0.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().place(x=300, y=40, width=300, height=200)
        self.fig.tight_layout(pad=0) 

        self.sensor_values = []
        self.line_border = None

        self.update_graph()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def nowBorder(self):
        print("WDS/LBVal")
        ser.write(f'WDS/LBVal'.encode())
    
    def updateBorder(self):
        global nowlineBorder
        self.label3.config(text=nowlineBorder)

    def on_closing(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.root.destroy()

    def lineflf(self):
        WDSSerialMode = 0
        ser.write(f'WDS/LSetflf'.encode())

    def linefrr(self):
        WDSSerialMode = 0
        ser.write(f'WDS/LSetfrr'.encode())

    def linebll(self):
        WDSSerialMode = 0
        ser.write(f'WDS/LSetbll'.encode())

    def linebrb(self):
        WDSSerialMode = 0
        ser.write(f'WDS/LSetbrb'.encode())

    def update_graph(self):
        if self.root.winfo_exists():
            # センサの値をlineSetingから取得
            self.sensor_values = lineSeting  # 最新の10個の値を取得
            self.line.set_data(range(len(self.sensor_values)), self.sensor_values)
            self.ax.set_xlim(0, 20)
            self.ax.set_ylim(0, 255)
            if self.line_border is not None:
                self.line_border.remove()
            self.line_border = self.ax.axhline(y=lineBorder, color='#84ffff', linestyle='-', linewidth=0.8)
            self.canvas.draw()
            self.updateBorder()
            # 1000ミリ秒（1秒）ごとにupdate_graphを呼び出す
            self.after_id = self.root.after(100, self.update_graph)

class RPprogram:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("中継RPプログラム")
        self.root.geometry("650x395")
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=30, width=90)
        self.text_area.place(x=0,y=0)
        with open('WDSfile/program/RPprogram.txt', 'r', encoding='utf-8') as file:
            self.text = file.read()
        self.text_area.insert(tk.END, self.text)
        self.text_area.config(state=tk.DISABLED)
        self.root.mainloop()

class myposition:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WDS/自己位置")
        self.root.geometry("750x400")

        self.marker = [{"x":0, "y":0} for i in range(16)]

        self.canvas = tk.Canvas(self.root, width=750, height=650)
        self.canvas.place(x=0, y=0)

        self.canvas.create_rectangle(500, 50, 682, 279, fill="#006600")
        self.canvas.create_oval(500+88, 50+112, 500+94, 50+118, fill="#0000FF")
        self.labe1 = tk.Label(self.root, text="LiDAR")
        self.labe1.place(x=10, y=10)
        self.labe2 = tk.Label(self.root, text="ロボット推定位置")
        self.labe2.place(x=500, y=10)
        self.labelx = tk.Label(self.root, text="X：")
        self.labelx.place(x=500, y=300)
        self.labely = tk.Label(self.root, text="Y：")
        self.labely.place(x=500, y=320)
        self.labelv = tk.Label(self.root, text="V：")
        self.labelv.place(x=500, y=340)
        self.labelr = tk.Label(self.root, text="r：")
        self.labelr.place(x=500, y=360)
        self.but1 = tk.Button(self.root, text="接続", command=lambda: self.putButton())
        self.but1.place(x=100, y=10)
        self.but2 = tk.Button(self.root, text="更新", command=lambda: self.putbutton2())
        self.but2.place(x=500, y=10)

        self.bars = []
        self.labels = []

        for i in range(16):
            angle = (16-i+3) * 22.5  # 16方位の角度
            x1 = 200
            y1 = 200
            x2 = 200 + 155 * math.cos(math.radians(angle + 180))  # 反対側のX座標
            y2 = 200 - 155 * math.sin(math.radians(angle + 180))  # 反対側のY座標
            lx = 190 + 160 * math.cos(math.radians(angle + 180)) 
            ly = 190 - 160 * math.sin(math.radians(angle + 180)) 
            bx = 200 - 200/1.33 * math.cos(math.radians(angle))
            by = 200 + 200/1.33 * math.sin(math.radians(angle))
            barback = self.canvas.create_line(x1, y1, bx, by, fill="#666666", width=5)

            # バーを作成
            bar = self.canvas.create_line(x1, y1, x2, y2, fill="#000000", width=5)
            self.bars.append(bar)



            # ラベルを作成
            label = tk.Label(self.root, text="0", fg="#000000",font=("", 10))
            label.place(x=lx, y=ly)
            self.labels.append(label)

        self.update_bars()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        global WDSSerialMode
        WDSSerialMode = 0
        self.root.destroy()

    def putButton(self):
        global WDSSerialMode
        if WDSSerialMode != 2:
            WDSSerialMode = 2
            self.but1.config(text="切断")
            self.but2.config(text="接続")
        else:
            WDSSerialMode = 0
            self.but1.config(text="接続")
    
    def putbutton2(self):
        global WDSSerialMode
        if WDSSerialMode != 3:
            WDSSerialMode = 3
            self.but2.config(text="切断")
            self.but1.config(text="接続")
        else:
            WDSSerialMode = 0
            self.but2.config(text="接続")
    
    def update_bars(self):
        if self.root.winfo_exists():
            self.canvas.delete("triangle")
            for i in range(16):
                value = cameraLIDAR[i]
                angle = (16-i+3) * 22.5
                x1 = 200
                y1 = 200
                x2 = 200 - value/1.33 * math.cos(math.radians(angle))
                y2 = 200 + value/1.33 * math.sin(math.radians(angle))
                self.marker[i]["x"] = x2
                self.marker[i]["y"] = y2
                # バーの色を更新
                self.canvas.coords(self.bars[i], x1, y1, x2, y2)
                self.canvas.itemconfig(self.bars[i], fill="#00FF00")

                # ラベルの値を更新
                self.labels[i].config(text=str(value))

            for i in range(16):
                next_i = (i + 1) % 16
                points = [200, 200, self.marker[i]["x"], self.marker[i]["y"], self.marker[next_i]["x"], self.marker[next_i]["y"]]
                self.canvas.create_polygon(points, fill="#00FF00",tags="triangle")

            self.labelx.config(text=f"X：{mypositionVal[0]:.2f}")
            self.labely.config(text=f"Y：{mypositionVal[1]:.2f}")
            self.labelv.config(text=f"V：{mypositionVal[2]:.2f}")
            self.labelr.config(text=f"r：{mypositionVal[3]:.2f}")

            self.root.after(100, self.update_bars)  # 100ミリ秒ごとに更新

# 他のコードはそのまま

def update_ports():
    portSet.delete(0, tk.END)
    ports = serial.tools.list_ports.comports()
    port_list = [port.device for port in ports]

    if not port_list:
        portSet.add_command(label="ポートが見つかりません", state=tk.DISABLED)
        portSet.add_separator()
        portSet.add_command(label="更新", command=update_ports)
    else:
        for port in port_list:
            label = port
            if port == serialPort:
                label = f"✔ {port}"
            portSet.add_command(label=label, command=lambda p=port: select_port(p))

        portSet.add_separator()
        portSet.add_command(label="更新", command=update_ports)

def select_port(port):
    global serialPort
    global ser
    global mainStop
    if serialPort != None:
        ser.close()
    messagebox.showinfo("情報", f"{port}が選択されました。")
    ser = serial.Serial(f"{port}", 38400)  # シリアル通信設定
    serialPort = port
    with open(PORT_FILE_PATH, 'w') as file:
        file.write(port)
    if mainStop:
        mainStop=False
        main()

def load_port_from_file():
    if os.path.exists(PORT_FILE_PATH):
        with open(PORT_FILE_PATH, 'r') as file:
            return file.read().strip()
    return None

def try_reconnect_last_port():
    last_port = load_port_from_file()
    if last_port:
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if last_port in ports:
            global serialPort
            global ser
            global mainStop
            if serialPort != None:
                ser.close()
            ser = serial.Serial(f"{last_port}", 38400)  # シリアル通信設定
            serialPort = last_port
            print("a")
            if mainStop:
                mainStop=False
                main()
    if mainStop:
        root.after(1000, try_reconnect_last_port)

def reconnect_serial_port():
    global serialPort
    global ser
    global mainStop
    try:
        last_port = load_port_from_file()
        if last_port:
            ser = serial.Serial(f"{last_port}", 38400, timeout=1)  # シリアル通信設定
            serialPort = last_port
            mainStop = False
            print("b")
    except serial.SerialException as e:
        pass  # 5秒後に再試行

def sensorShowDisplay(data):
    datalist = data.split("/")
    if len(datalist[0])+2 == len(datalist):
        for i in range(len(datalist[0])):
            if datalist[0][i] == "L":
                lineValue = datalist[i+1].split(",")
                showLineBL1.config(text=lineValue[0])
                showLineFL1.config(text=lineValue[1])
                showLineFR1.config(text=lineValue[2])
                showLineBR1.config(text=lineValue[3])
            if datalist[0][i] == "M":
                MoterValue = datalist[i + 1].split(",")
                if MoterValue[0][0] == "f":
                    showMotBL1.config(text=str(int(MoterValue[0][1:], 16)))
                else:
                    showMotBL1.config(text="-"+str(int(MoterValue[0][1:], 16)))
                if MoterValue[1][0] == "f":
                    showMotFL1.config(text=str(int(MoterValue[1][1:], 16)))
                else:
                    showMotFL1.config(text="-"+str(int(MoterValue[1][1:], 16)))
                if MoterValue[2][0] == "f":
                    showMotBR1.config(text=str(int(MoterValue[2][1:], 16)))
                else:
                    showMotBR1.config(text="-"+str(int(MoterValue[2][1:], 16)))
                if MoterValue[3][0] == "f":
                    showMotFR1.config(text=str(int(MoterValue[3][1:], 16)))
                else:
                    showMotFR1.config(text="-"+str(int(MoterValue[3][1:], 16)))
            if datalist[0][i] == "J":
                jairoValue = datalist[i + 1]
                showJai1.config(text=jairoValue)
            if datalist[0][i] == "Y":
                yellowGoalValue = datalist[i + 1]
                senserR1[16] = int(yellowGoalValue)
                drawyellowGoalRad()
            if datalist[0][i] == "B":
                blueGoalValue = datalist[i + 1]
                senserR1[15] = int(blueGoalValue)
                drawblueGoalRad()
            if datalist[0][i] == "R":
                ballValue = datalist[i + 1]
                senserR1[14] = int(ballValue)
                drawBallRad()
            if datalist[0][i] == "G":
                goRadValue = datalist[i + 1]
                senserR1[17] = int(goRadValue)
                drawgoRad()
            if datalist[0][i] == "D":
                senserR1[18] = int(datalist[i + 1])
                showDirection1.config(text=F"D: {datalist[i + 1]}")

                

def SSAMode():
    global WDSSerialMode
    if connectBut1["text"] == "接続":
        WDSSerialMode = 1
        connectBut1["text"] = "切断"
        connectBut1["fg"] = "#FF0000"
    else:
        WDSSerialMode = 0
        connectBut1["text"] = "接続"
        connectBut1["fg"] = "#AAFFAA"

def serialRecive(data):
    global urlogTxt
    global lineSeting
    global lineBorder
    urlogTxt = urlogTxt + data.split("\n")
    if len(urlogTxt) > 20:
        urlogTxt = urlogTxt[-20:]
    filterStr = [element for element in urlogTxt if "Sy/SVMo/" in element[0:8]]
    if len(filterStr) > 0:
        sensorShowDisplay(filterStr[-1][8:])
    filterStr = [element for element in urlogTxt if "WDS/LSVal/" in element[0:10]]
    if len(filterStr) > 0:
        lineSeting.append(int(filterStr[-1][10:]))
        if len(lineSeting) > 20:
            lineSeting.pop(0)
    filterStr = [element for element in urlogTxt if "WDS/LBorV/" in element[0:10]]
    if len(filterStr) > 0:
        lineBorder = int(filterStr[-1][10:])
    filterStr = [element for element in urlogTxt if "WDS/LBVals/" in element[0:11]]
    if len(filterStr) > 0:
        global nowlineBorder
        nowlineBorder = filterStr[-1][11:]
    filterStr = [element for element in urlogTxt if "WDS/LiDVals/" in element[0:12]]
    if len(filterStr) > 0:
        global cameraLIDAR
        cameraLIDAR = list(map(int, filterStr[-1][12:].split(",")))
    filterStr = [element for element in urlogTxt if "WDS/MyPos/" in element[0:10]]
    if len(filterStr) > 0:
        global mypositionVal
        mypositionVal = list(map(float, filterStr[-1][10:].split(",")))


def main():
    global mainStop
    global urtext
    global rootAfterTask
    global serial_monitor_instance
    try:
        if serialPort is not None:
            if ser.in_waiting > 0:
                urtext = str(ser.readline())
                print(urtext[2:-5])
                serialRecive(urtext[2:-5])
                add_serialtext(urtext[2:-5])
    except serial.SerialException as e:
        mainStop = True
        reconnect_serial_port()
    except Exception as e:
        mainStop = True
        messagebox.showerror("エラー", f"エラーが発生しました: {e}")
    if WDSSerialMode == 1:
        try:
            ser.write(f'WDS/SSA'.encode())
        except serial.SerialException as e:
            mainStop = True
            reconnect_serial_port()
    if WDSSerialMode == 2:
        try:
            ser.write(f'WDS/LiDVal'.encode())
        except serial.SerialException as e:
            mainStop = True
            reconnect_serial_port()
    if WDSSerialMode == 3:
        try:
            ser.write(f'WDS/MyPo'.encode())
        except serial.SerialException as e:
            mainStop = True
            reconnect_serial_port()
    if root.winfo_exists():
        rootAfterTask = root.after(10, main)

def open_serial_monitor():
    global serial_monitor_instance
    serial_monitor_instance = serialMoniter()

def checkBoxChenge():
    if sensershowR1[0].get():
        showTofL1.place(x=48, y=208);showTofF1.place(x=200, y=70);showTofR1.place(x=345, y=208);showTofB1.place(x=200, y=348)
    else:
        showTofL1.place_forget();showTofF1.place_forget();showTofR1.place_forget();showTofB1.place_forget()
    if sensershowR1[1].get():
        showLineFL1.place(x=95,y=123);showLineFR1.place(x=305,y=123);showLineBR1.place(x=305,y=293);showLineBL1.place(x=95,y=293)
    else:
        showLineFL1.place_forget();showLineFR1.place_forget();showLineBR1.place_forget();showLineBL1.place_forget()
    if sensershowR1[2].get():
        showMotFL1.place(x=155,y=188);showMotFR1.place(x=245,y=188);showMotBR1.place(x=245,y=238);showMotBL1.place(x=155,y=238)
    else:
        showMotFL1.place_forget();showMotFR1.place_forget();showMotBR1.place_forget();showMotBL1.place_forget()
    if sensershowR1[3].get():
        showJai1.place(x=200, y=213)
    else:
        showJai1.place_forget()
    if sensershowR2[0].get():
        showTofL2.place(x=443,y=208);showTofF2.place(x=595,y=70);showTofR2.place(x=743,y=208);showTofB2.place(x=595,y=348)
    else:
        showTofL2.place_forget();showTofF2.place_forget();showTofR2.place_forget();showTofB2.place_forget()
    if sensershowR2[1].get():
        showLineFL2.place(x=490,y=123);showLineFR2.place(x=700,y=123);showLineBR2.place(x=700,y=293);showLineBL2.place(x=490,y=293)
    else:
        showLineFL2.place_forget();showLineFR2.place_forget();showLineBR2.place_forget();showLineBL2.place_forget()
    if sensershowR2[2].get():
        showMotFL2.place(x=550,y=188);showMotFR2.place(x=640,y=188);showMotBR2.place(x=640,y=238);showMotBL2.place(x=550,y=238)
    else:
        showMotFL2.place_forget();showMotFR2.place_forget();showMotBR2.place_forget();showMotBL2.place_forget()
    if sensershowR2[3].get():
        showJai2.place(x=595,y=213)
    else:
        showJai2.place_forget()

def drawBallRad():
    global ballCanvas1
    global ballCanvas2
    if ballCanvas1 != None:
        canvas.delete(ballCanvas1)
    if ballCanvas2 != None:
        canvas.delete(ballCanvas2)
    if abs(senserR1[14] < 181):
        angle = math.radians(senserR1[14])  # 角度をラジアンに変換   
        center_x, center_y = 213, 223  # 中心座標
        radius = 178  # 大きな円の半径
        small_radius = 10  # 小さな円の半径
        x = center_x + radius * math.sin(angle)
        y = center_y - radius * math.cos(angle) 
        ballCanvas1 = canvas.create_oval(x - small_radius, y - small_radius, x + small_radius, y + small_radius, fill="#ff4500")

    if abs(senserR2[14] < 181):
        angle = math.radians(senserR2[14])
        center_x, center_y = 613, 223
        radius = 178
        small_radius = 10
        x = center_x + radius * math.sin(angle)
        y = center_y - radius * math.cos(angle)
        ballCanvas2 = canvas.create_oval(x - small_radius, y - small_radius, x + small_radius, y + small_radius, fill="#ff4500")

    showRad1.config(text=f"R1: {senserR1[14]}")

def drawblueGoalRad():
    global blueGoalCanvas1
    global blueGoalCanvas2
    if blueGoalCanvas1 != None:
        canvas.delete(blueGoalCanvas1)
    if blueGoalCanvas2 != None:
        canvas.delete(blueGoalCanvas2)
    if senserR1[15] < 181:
        angle = math.radians(senserR1[15])  # 角度をラジアンに変換
        center_x, center_y = 213, 223  # 中心座標
        radius = 178  # 大きな円の半径
        small_radius = 10  # 小さな円の半径
        x = center_x + radius * math.sin(angle)
        y = center_y - radius * math.cos(angle) 
        blueGoalCanvas1 = canvas.create_line(center_x, center_y, x, y, fill="#0000ff", width=2)

    if senserR2[15] < 181:
        angle = math.radians(senserR2[15])
        center_x, center_y = 613, 223
        radius = 178
        small_radius = 10
        x = center_x + radius * math.sin(angle)
        y = center_y - radius * math.cos(angle)
        blueGoalCanvas2 = canvas.create_line(center_x, center_y, x, y, fill="#0000ff", width=2)

def drawyellowGoalRad():
    global yellowGoalCanvas1
    global yellowGoalCanvas2
    if yellowGoalCanvas1 != None:
        canvas.delete(yellowGoalCanvas1)
    if yellowGoalCanvas2 != None:
        canvas.delete(yellowGoalCanvas2)
    if senserR1[16] < 181:
        angle = math.radians(senserR1[16])  # 角度をラジアンに変換
        center_x, center_y = 213, 223  # 中心座標
        radius = 178  # 大きな円の半径
        small_radius = 10  # 小さな円の半径
        x = center_x + radius * math.sin(angle)
        y = center_y - radius * math.cos(angle) 
        yellowGoalCanvas1 = canvas.create_line(center_x, center_y, x, y, fill="#ffff00", width=2)

    if senserR2[16] < 181:
        angle = math.radians(senserR2[16])
        center_x, center_y = 613, 223
        radius = 178
        small_radius = 10
        x = center_x + radius * math.sin(angle)
        y = center_y - radius * math.cos(angle)
        yellowGoalCanvas2 = canvas.create_line(center_x, center_y, x, y, fill="#ffff00", width=2)

def drawgoRad():
    global goRadCanvas1
    global goRadCanvas2
    if goRadCanvas1 != None:
        canvas.delete(goRadCanvas1)
    if goRadCanvas2 != None:
        canvas.delete(goRadCanvas2)
    if senserR1[17] < 181:
        angle = math.radians(senserR1[17])
        center_x, center_y = 213, 223
        radius = 178
        small_radius = 10
        x = center_x + radius * math.sin(angle)
        y = center_y - radius * math.cos(angle)
        goRadCanvas1 = canvas.create_line(center_x, center_y, x, y, fill="#ff00ff", width=2)
    
    if senserR2[17] < 181:
        angle = math.radians(senserR2[17])
        center_x, center_y = 613, 223
        radius = 178
        small_radius = 10
        x = center_x + radius * math.sin(angle)
        y = center_y - radius * math.cos(angle)
        goRadCanvas2 = canvas.create_line(center_x, center_y, x, y, fill="#ff00ff", width=2)

def add_serialtext(text):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, text + "\n")
    text_area.see(tk.END)
    text_area.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Tachyon WDS")
root.geometry("850x600")
root.iconbitmap(default='WDSfile/images/icon.ico')
menuBar = tk.Menu(root)
root.config(menu=menuBar)
root.configure(bg='#080613')
rootAfterTask = None
#メニューバー
secMenu = tk.Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="セキュリティー", menu=secMenu)
secMenu.add_command(label="ロボット共通鍵新規登録", command=lambda: addRobot(), state=tk.DISABLED)  # 無効化
secMenu.add_command(label="ロボット共通鍵登録情報", command=lambda: roboInformation(), state=tk.DISABLED)  # 無効化
exportMenu = tk.Menu(menuBar, tearoff=0, postcommand=update_ports)  # ポート情報を更新
menuBar.add_cascade(label="通信", menu=exportMenu)
portSet = tk.Menu(exportMenu, tearoff=0)
exportMenu.add_cascade(label="ポート設定", menu=portSet)
exportMenu.add_command(label="ターミナル", command=lambda: terminal(),state=tk.DISABLED)  # 無効化
exportMenu.add_command(label="ログ", command=lambda: log(),state=tk.DISABLED)  # 無効化
exportMenu.add_command(label="シリアルモニター", command=open_serial_monitor,state=tk.DISABLED)  # 無効化
comMenu = tk.Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="コマンド", menu=comMenu, state=tk.DISABLED)  # 無効化
comMenu.add_command(label="コマンド一覧", command=lambda: commandlist())
comMenu.add_command(label="コマンド編集", command=lambda: commandAdd())
valMenu = tk.Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="変数", menu=valMenu, state=tk.DISABLED)  # 無効化
valMenu.add_command(label="変数確認")
valMenu.add_command(label="変数変更")
valMenu.add_command(label="変数アドレス")
paneMenu = tk.Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="操作パネル", menu=paneMenu)
paneMenu.add_command(label="位置移動パネル", state=tk.DISABLED)  # 無効化
paneMenu.add_command(label="手動操作パネル", state=tk.DISABLED)  # 無効化
paneMenu.add_command(label="コマンド操作パネル", state=tk.DISABLED)  # 無効化
paneMenu.add_command(label="ラインセンサパネル", command=lambda: lineSensorPanel(root))
paneMenu.add_command(label="自己位置推定パネル", command=lambda: myposition())  # 無効化
programMenu = tk.Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="プログラム", menu=programMenu)
programMenu.add_command(label="中継RPのプログラム", command=lambda: RPprogram())

backGroundImage = tk.PhotoImage(file="WDSfile/images/roboDashboard.png")
line_image = tk.PhotoImage(file="WDSfile/images/lineSensor.png")
canvas = tk.Canvas(bg='#080613', borderwidth=0)
canvas.pack(fill=tk.BOTH, expand=True)
canvas.create_image(0, 50, image=backGroundImage, anchor=tk.NW)

connectBut1 = tk.Button(text="接続", bg="#080613", fg="#AAFFAA",borderwidth=3, font=("",13), command=lambda: SSAMode())
connectBut1.place(x=190,y=420)
connectBut2 = tk.Button(text="接続", bg="#080613", fg="#AAFFAA",borderwidth=3, font=("",13))
connectBut2.place(x=590,y=420)

showTofL1 = tk.Label(text=str(senserR1[0]),bg="#080613",fg="#FFFFFF",font=("",15))
showTofL1.place(x=48,y=208)
showTofF1 = tk.Label(text=str(senserR1[1]),bg="#080613",fg="#FFFFFF",font=("",15))
showTofF1.place(x=200,y=70)
showTofR1 = tk.Label(text=str(senserR1[2]),bg="#080613",fg="#FFFFFF",font=("",15))
showTofR1.place(x=345,y=208)
showTofB1 = tk.Label(text=str(senserR1[3]),bg="#080613",fg="#FFFFFF",font=("",15))
showTofB1.place(x=200,y=348)
showLineFL1 = tk.Label(text=str(senserR1[4]),bg="#080613",fg="#FF0000",font=("",15))
showLineFL1.place(x=95,y=123)
showLineFR1 = tk.Label(text=str(senserR1[5]),bg="#080613",fg="#FF0000",font=("",15))
showLineFR1.place(x=305,y=123)
showLineBR1 = tk.Label(text=str(senserR1[6]),bg="#080613",fg="#FF0000",font=("",15))
showLineBR1.place(x=305,y=293)
showLineBL1 = tk.Label(text=str(senserR1[7]),bg="#080613",fg="#FF0000",font=("",15))
showLineBL1.place(x=95,y=293)
showMotFL1 = tk.Label(text=str(senserR1[8]),bg="#080613",fg="#FFFF00",font=("",15))
showMotFL1.place(x=155,y=188)
showMotFR1 = tk.Label(text=str(senserR1[9]),bg="#080613",fg="#FFFF00",font=("",15))
showMotFR1.place(x=245,y=188)
showMotBR1 = tk.Label(text=str(senserR1[10]),bg="#080613",fg="#FFFF00",font=("",15))
showMotBR1.place(x=245,y=238)
showMotBL1 = tk.Label(text=str(senserR1[11]),bg="#080613",fg="#FFFF00",font=("",15))
showMotBL1.place(x=155,y=238)
showJai1 = tk.Label(text=str(senserR1[12]),bg="#080613",fg="#00FFFF",font=("",15))
showJai1.place(x=200,y=213)
showDirection1 = tk.Label(text=f"D: {str(senserR1[18])}",bg="#FF0000",fg="#FFFFFF",font=("",15,"bold"))
showDirection1.place(x=10,y=50)
showRad1 = tk.Label(text=f"R: {str(senserR2[14])}",bg="#FF8800",fg="#FFFFFF",font=("",15,"bold"))
showRad1.place(x=10,y=80)

showTofL2 = tk.Label(text=str(senserR2[0]),bg="#080613",fg="#FFFFFF",font=("",15))
showTofL2.place(x=443,y=208)
showTofF2 = tk.Label(text=str(senserR2[1]),bg="#080613",fg="#FFFFFF",font=("",15))
showTofF2.place(x=595,y=70)
showTofR2 = tk.Label(text=str(senserR2[2]),bg="#080613",fg="#FFFFFF",font=("",15))
showTofR2.place(x=743,y=208)
showTofB2 = tk.Label(text=str(senserR2[3]),bg="#080613",fg="#FFFFFF",font=("",15))
showTofB2.place(x=595,y=348)
showLineFL2 = tk.Label(text=str(senserR2[4]),bg="#080613",fg="#FF0000",font=("",15))
showLineFL2.place(x=490,y=123)
showLineFR2 = tk.Label(text=str(senserR2[5]),bg="#080613",fg="#FF0000",font=("",15))
showLineFR2.place(x=700,y=123)
showLineBR2 = tk.Label(text=str(senserR2[6]),bg="#080613",fg="#FF0000",font=("",15))
showLineBR2.place(x=700,y=293)
showLineBL2 = tk.Label(text=str(senserR2[7]),bg="#080613",fg="#FF0000",font=("",15))
showLineBL2.place(x=490,y=293)
showMotFL2 = tk.Label(text=str(senserR2[8]),bg="#080613",fg="#FFFF00",font=("",15))
showMotFL2.place(x=550,y=188)
showMotFR2 = tk.Label(text=str(senserR2[9]),bg="#080613",fg="#FFFF00",font=("",15))
showMotFR2.place(x=640,y=188)
showMotBR2 = tk.Label(text=str(senserR2[10]),bg="#080613",fg="#FFFF00",font=("",15))
showMotBR2.place(x=640,y=238)
showMotBL2 = tk.Label(text=str(senserR2[11]),bg="#080613",fg="#FFFF00",font=("",15))
showMotBL2.place(x=550,y=238)
showJai2 = tk.Label(text=str(senserR2[12]),bg="#080613",fg="#00FFFF",font=("",15))
showJai2.place(x=595,y=213)
showDirection2 = tk.Label(text=f"D: {str(senserR2[18])}",bg="#FF0000",fg="#FFFFFF",font=("",15,"bold"))
showDirection2.place(x=400,y=50)

sensershowR1 = [tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar()]
sensershowR1[0].set(False);sensershowR1[1].set(True);sensershowR1[2].set(True);sensershowR1[3].set(True);sensershowR1[4].set(True)
sensershowR2 = [tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar()]
sensershowR2[0].set(False);sensershowR2[1].set(True);sensershowR2[2].set(True);sensershowR2[3].set(True);sensershowR2[4].set(True)
checkButtonR1_1 = tk.Checkbutton(root, text="距離センサ",variable=sensershowR1[0],command=checkBoxChenge,state=tk.DISABLED)
checkButtonR1_1.place(x=0,y=0)
checkButtonR1_2 = tk.Checkbutton(root, text="ラインセンサ",variable=sensershowR1[1],command=checkBoxChenge)
checkButtonR1_2.place(x=80,y=0)
checkButtonR1_3 = tk.Checkbutton(root, text="モーター",variable=sensershowR1[2],command=checkBoxChenge)
checkButtonR1_3.place(x=160,y=0)
checkButtonR1_4 = tk.Checkbutton(root, text="角度",variable=sensershowR1[3],command=checkBoxChenge)
checkButtonR1_4.place(x=220,y=0)
checkButtonR2_1 = tk.Checkbutton(root, text="距離センサ",variable=sensershowR2[0],command=checkBoxChenge,state=tk.DISABLED)
checkButtonR2_1.place(x=400,y=0)
checkButtonR2_2 = tk.Checkbutton(root, text="ラインセンサ",variable=sensershowR2[1],command=checkBoxChenge)
checkButtonR2_2.place(x=480,y=0)
checkButtonR2_3 = tk.Checkbutton(root, text="モーター",variable=sensershowR2[2],command=checkBoxChenge)
checkButtonR2_3.place(x=560,y=0)
checkButtonR2_4 = tk.Checkbutton(root, text="角度",variable=sensershowR2[3],command=checkBoxChenge)
checkButtonR2_4.place(x=620,y=0)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, width=118, bg="#191970", fg="#FFFF00", insertbackground='white')
text_area.place(x=0, y=460)
text_area.insert(tk.END, "-----------シリアルモニター-----------\n")
text_area.config(state=tk.DISABLED)

drawBallRad()
drawblueGoalRad()
drawyellowGoalRad()
drawgoRad()
checkBoxChenge()
main()

def rootOnClosing():
    if rootAfterTask is not None:
        root.after_cancel(rootAfterTask)
    root.destroy()

    sys.exit()

root.protocol("WM_DELETE_WINDOW", rootOnClosing)

try_reconnect_last_port()

root.mainloop()