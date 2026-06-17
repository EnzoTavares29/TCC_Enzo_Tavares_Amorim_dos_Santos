import tkinter as tk


class JointSetupView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(
            self,
            text="Definição da geometria da junta",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        form = tk.Frame(self)
        form.pack(pady=10)

        tk.Label(form, text="Número de parafusos").grid(row=0, column=0, sticky="e")
        tk.Label(form, text="Largura da junta [mm]").grid(row=1, column=0, sticky="e")
        tk.Label(form, text="Altura da junta [mm]").grid(row=2, column=0, sticky="e")

        self.n_entry = tk.Entry(form, width=10)
        self.w_entry = tk.Entry(form, width=10)
        self.h_entry = tk.Entry(form, width=10)

        self.n_entry.grid(row=0, column=1)
        self.w_entry.grid(row=1, column=1)
        self.h_entry.grid(row=2, column=1)

        tk.Button(
            self,
            text="Avançar",
            command=self.confirm
        ).pack(pady=10)

        tk.Button(
            self,
            text="Voltar",
            command=self.controller.back
        ).pack()

        tk.Button(
            self,
            text="Exemplo COEMI",
            font=("Arial", 8),
            fg="gray40",
            command=self.controller.load_tester_example
        ).pack(pady=2)

    def confirm(self):
        n = int(self.n_entry.get())
        w = float(self.w_entry.get())
        h = float(self.h_entry.get())

        self.controller.set_joint_geometry(n, w, h)
