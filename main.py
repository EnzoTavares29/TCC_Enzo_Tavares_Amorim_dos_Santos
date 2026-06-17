import tkinter as tk
from controllers.app_controller import AppController

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dimensionamento de Junta Parafusada")
    root.geometry("900x700")
    AppController(root)
    root.mainloop()
