import tkinter as tk


class ResultsView(tk.Frame):
    """
    Tela exclusiva para apresentação dos resultados
    """

    def __init__(self, master, controller, result_text):
        super().__init__(master)
        self.controller = controller

        # ================= TÍTULO =================
        tk.Label(
            self,
            text="Resultados do Dimensionamento",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        # ================= RESULTADOS =================
        result_box = tk.Text(
            self,
            width=70,
            height=20,
            font=("Courier", 10)
        )
        result_box.pack(padx=10, pady=10)
        result_box.insert("1.0", result_text)
        result_box.config(state="disabled")

        # ================= NAVEGAÇÃO =================
        nav = tk.Frame(self)
        nav.pack(pady=10)

        tk.Button(
            nav,
            text="Refazer dimensionamento",
            width=25,
            command=self.controller.go_to_dimensioning
        ).pack(side="left", padx=5)

        tk.Button(
            nav,
            text="Voltar para carregamento",
            width=25,
            command=self.controller.go_to_load_definition
        ).pack(side="left", padx=5)

        tk.Button(
            nav,
            text="Menu inicial",
            width=25,
            command=self.controller.back_to_setup
        ).pack(side="left", padx=5)
