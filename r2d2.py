import tkinter as tk
from tkinter import PhotoImage
import pygame
import threading

pygame.mixer.init()

root = tk.Tk()
root.title("R2-D2")
root.geometry("900x600")
root.resizable(False, False)

# FONDO E IMAGENES
fondo_img = PhotoImage(file="fondo_espacio.png")
r2_right = PhotoImage(file="r2_normal.png")
r2_left = PhotoImage(file="r2_normal_left.png")

r2_saludo_gif = [PhotoImage(file="r2_saludo.gif", format=f"gif - {i}") for i in range(8)]
r2_dance_gif = [PhotoImage(file="r2_dance.gif", format=f"gif - {i}") for i in range(12)]
r2_angry_gif = [PhotoImage(file="r2_angry.gif", format=f"gif - {i}") for i in range(9)]

# SONIDOS
sound_greet = "r2_greet.wav"
sound_dance = "r2_dance.wav"
sound_angry = "r2_angry.wav"

# PANTALLA
canvas = tk.Canvas(root, width=900, height=600, highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=fondo_img, anchor="nw")

# R2D2
r2_x = 450
r2_y = 450
r2_width = r2_right.width()
r2_height = r2_right.height()
r2_label = canvas.create_image(r2_x, r2_y, image=r2_right)
direction = 1
speed = 10
bailando = False
dance_channel = None
moving = False
target_x = r2_x

# FUNCIONES DE SONIDO
def play_sound(sound_file, loop=False):
    def play():
        s = pygame.mixer.Sound(sound_file)
        if loop:
            s.play(-1)
        else:
            s.play()
        return s
    t = threading.Thread(target=play)
    t.start()

# GIFS
def reproducir_gif(frames, sonido=None, loop=False, callback=None, indice=0):
    if loop and not bailando:
        if callback:
            callback()
        return

    if indice == 0 and sonido and loop:
        global dance_channel
        dance_channel = pygame.mixer.Sound(sonido)
        dance_channel.play(-1)
    elif indice == 0 and sonido and not loop:
        play_sound(sonido, loop=False)

    if indice < len(frames):
        canvas.itemconfig(r2_label, image=frames[indice])
        root.after(100, lambda: reproducir_gif(frames, sonido, loop, callback, indice + 1))
    else:
        if loop:
            root.after(50, lambda: reproducir_gif(frames, sonido=None, loop=True, callback=callback, indice=0))
        elif callback:
            callback()

# ACCIONES
def saludar():
    if bailando:
        return
    reproducir_gif(r2_saludo_gif, sonido=sound_greet, loop=False, callback=restaurar_imagen)

def enojarse():
    if bailando:
        return
    reproducir_gif(r2_angry_gif, sonido=sound_angry, loop=False, callback=restaurar_imagen)

def restaurar_imagen():
    canvas.itemconfig(r2_label, image=r2_right if direction == 1 else r2_left)

# MOVIMIENTO
def mover_a_objetivo():
    global r2_x, direction, moving
    if not moving or bailando:
        return

    if abs(r2_x - target_x) <= speed:
        r2_x = target_x
        moving = False
        canvas.coords(r2_label, r2_x, r2_y)
        restaurar_imagen()
        if action_after_move == "saludar":
            saludar()
        elif action_after_move == "enojarse":
            enojarse()
        return

    if target_x < r2_x:
        direction = -1
        r2_x -= speed
        canvas.itemconfig(r2_label, image=r2_left)
    else:
        direction = 1
        r2_x += speed
        canvas.itemconfig(r2_label, image=r2_right)

    canvas.coords(r2_label, r2_x, r2_y)
    root.after(50, mover_a_objetivo)

# AL HACER CLIC
def click_en_r2(event):
    global target_x, moving, action_after_move

    if bailando:
        return

    # LIMITES DE MOVIMIENTO
    left = r2_x - r2_width // 2
    right = r2_x + r2_width // 2
    top = r2_y - r2_height // 2
    bottom = r2_y + r2_height // 2

    # VER SI EL CLIC ESTA DENTRO DEL AREA DE R2D2
    if left <= event.x <= right and top <= event.y <= bottom:
        cabeza_limite = top + r2_height // 3
        action_after_move = "saludar" if event.y <= cabeza_limite else "enojarse"
        target_x = r2_x  # SI ESTA ENCIMA 
        moving = False
        if action_after_move == "saludar":
            saludar()
        else:
            enojarse()
    else:
        # SI ESTA FUERA MOVERSE HACIA ALLI
        target_x = event.x
        moving = True
        action_after_move = None
        mover_a_objetivo()

canvas.bind("<Button-1>", click_en_r2)

# BOTON DE BAILE
def alternar_baile():
    global bailando, dance_channel
    bailando = not bailando

    if bailando:
        boton_bailar.config(text="Dejar de bailar 🛑", bg="#FF4500")
        reproducir_gif(r2_dance_gif, sonido=sound_dance, loop=True, callback=restaurar_imagen)
    else:
        if dance_channel:
            dance_channel.stop()
        boton_bailar.config(text="Bailar 💃", bg="#32CD32")
        restaurar_imagen()

boton_bailar = tk.Button(root, text="Bailar 💃", command=alternar_baile,
                         bg="#32CD32", fg="white", font=("Arial", 12, "bold"), bd=0)
canvas.create_window(450, 550, window=boton_bailar)

root.mainloop()
