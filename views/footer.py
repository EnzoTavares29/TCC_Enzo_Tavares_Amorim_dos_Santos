import tkinter as tk


class Footer(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(
            self,
            text=(
                "Enzo Tavares — Engenharia Mecânica — Universidade Federal de Sergipe\n"
                "TCC: Dimensionamento de Juntas Parafusadas considerando "
                "Cisalhamento e Atrito"
            ),
            font=("Arial", 9),
            fg="gray"
        ).pack(pady=5)
