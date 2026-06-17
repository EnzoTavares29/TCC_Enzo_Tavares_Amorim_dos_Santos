import tkinter as tk


class LoadSelectionView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(
            self,
            text="Selecione o tipo de carregamento",
            font=("Arial", 12, "bold")
        ).pack(pady=20)

        tk.Button(
            self,
            text="Cisalhamento centrado",
            width=30,
            command=lambda: controller.set_load_type("centrado")
        ).pack(pady=5)

        tk.Button(
            self,
            text="Cisalhamento excêntrico no plano",
            width=30,
            command=lambda: controller.set_load_type("excêntrico no plano")
        ).pack(pady=5)
