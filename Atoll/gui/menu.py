import tkinter as tk
from tkinter import ttk
from game.enums import Player
from game.enums import GameMode

def open_menu():
    root = tk.Tk()
    root.title("Game Setup")
    root.geometry("300x250")

    board_size = tk.IntVar(value=9)
    game_mode = tk.StringVar(value="PVP")
    first_player = tk.StringVar(value="BLACK")

    ttk.Label(root, text="Board size").pack(pady=5)
    ttk.Combobox(root, values=[5, 7, 9], textvariable=board_size).pack()

    ttk.Label(root, text="Game mode").pack(pady=5)
    ttk.Radiobutton(root, text="Player vs Player", variable=game_mode, value="PVP").pack()
    ttk.Radiobutton(root, text="Player vs Computer", variable=game_mode, value="AI").pack()

    ttk.Label(root, text="First player").pack(pady=5)
    ttk.Radiobutton(root, text="Black", variable=first_player, value="BLACK").pack()
    ttk.Radiobutton(root, text="White", variable=first_player, value="WHITE").pack()

    start_clicked = tk.BooleanVar(value=False)

    def start():
        start_clicked.set(True)
        root.destroy()

    ttk.Button(root, text="Start Game", command=start).pack(pady=10)
    root.mainloop()

    return {
        "board_size": board_size.get(),
        "game_mode": GameMode.PVP if game_mode.get()=="PVP" else GameMode.AI,
        "first_player": Player.WHITE if first_player.get()=="WHITE" else Player.BLACK
    }
