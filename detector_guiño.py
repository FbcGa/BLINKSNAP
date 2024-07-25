# -*- coding: utf-8 -*-
"""
Created on Sun Nov 13 22:45:33 2022

@author: Fabricio
"""
import os
import cv2
import tkinter as tk
from PIL import Image, ImageTk
from tkinter.messagebox import showinfo
from datetime import datetime

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kiosco de Fotos")
        self.geometry("600x460+100+100")
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')
        self.cap = cv2.VideoCapture(0)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.statusbar = tk.Label(self, text="Listo…", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(self, width=width, height=height, borderwidth=1, relief=tk.SUNKEN)
        self.canvas.pack()
        
        self.eye_detected = False
        self.eye_not_detected_start = None
        self.window_open = False
        
        self.loop_camara()
     
    def loop_camara(self):
        if not self.window_open:
            ret, frame = self.cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, "Rostro Detectado", (x, y - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    roi_gray = gray[y:y + h, x:x + w]
                    roi_color = frame[y:y + h, x:x + w]
                    
                    eyes = self.eye_cascade.detectMultiScale(roi_gray, 2.2, 7)
                    
                    if len(eyes) == 1:
                        self.eye_detected = True
                        self.eye_not_detected_start = None
                    elif len(eyes) == 0 and self.eye_detected:
                        if self.eye_not_detected_start is None:
                            self.eye_not_detected_start = datetime.now()
                        elif (datetime.now() - self.eye_not_detected_start).total_seconds() >= 0.5:
                            self.take_picture()
                            self.eye_detected = False
                            self.eye_not_detected_start = None

                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                            
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=photo, anchor='nw')
                self.canvas.image = photo
            
        self.after(20, self.loop_camara)

    def take_picture(self):
        self.statusbar.config(text='Rostro detectado')
        ret, frame = self.cap.read()
        if ret:
            _, pos_x, pos_y = self.geometry().split("+")
            self.window_open = True
            Level_Window(self, pos_x, pos_y, frame)                 
            
    def close_app(self):
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()
       
class Level_Window(tk.Toplevel):
    def __init__(self, master, pos_x, pos_y, frame):
        super().__init__(master)
        self.master = master
        self.geometry(f"600x500+{int(pos_x)+100}+{int(pos_y)+100}")
        self.title("Multimedia Kiosk - Photo Preview")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        
        self.width, self.height = 600, 400
        
        self.canvas = tk.Canvas(self, width=self.width+20, height=self.height+20, 
                                borderwidth=1, relief=tk.SUNKEN, bg='#f2f2f2')
        self.canvas.pack()
        self.frame = frame
               
        frm1 = tk.LabelFrame(self, text="Visualización")
        frm2 = tk.Frame(self)
        frm1.pack(padx=10, pady=10)
        frm2.pack(padx=10, pady=10)
        
        #-----------------------frm1-------------------------------------
        self.canvas = tk.Canvas(frm1, width=self.width, height=self.height, 
                                borderwidth=1, relief=tk.SUNKEN)
        self.canvas.pack()
        
        #-----------------------frm2--------------------------------------
        self.btnSave = tk.Button(frm2, text="Guardar", font=("Arial", 12, "bold"), 
                                 width=24, command=self.SavePicture)
        
        self.btnDelete = tk.Button(frm2, text="Borrar", font=("Arial", 12, "bold"), 
                                   width=24, command=self.DropPicture)
                                    
        self.btnSave.grid(row=0, column=0, padx=5, pady=5)        
        self.btnDelete.grid(row=0, column=1, padx=5, pady=5)
        
        try:
            photo = ImageTk.PhotoImage(image=Image.fromarray(self.frame))
            self.canvas.create_image(0, 0, image=photo, anchor='nw')
            self.canvas.image = photo
        except Exception as e:
            print(f"Error al cargar la imagen: {e}") 

    def SavePicture(self):
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.frame = cv2.resize(self.frame, (self.width, self.height))
        filename = f"{datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(filename, self.frame)
        showinfo("Imagen Guardada", f"Guardada en {os.path.abspath(filename)}")
        self.close_window()
        
    def DropPicture(self):
        showinfo("Imagen Borrada", "La imagen ha sido borrada")
        self.close_window()
    
    def close_window(self):
        self.master.window_open = False
        self.destroy()
        
if __name__ == "__main__":
    app = App()
    app.mainloop()
