import tkinter as tk
from tkinter import ttk, messagebox

from loads.vector_load import VectorLoad


class LoadDefinitionView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(
            self,
            text="Definição do Carregamento (Vetorial)",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(self, text="Força Fx [kN]").grid(row=1, column=0, sticky="e")
        self.fx_entry = ttk.Entry(self)
        self.fx_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.fx_entry.insert(0, "0.0")

        tk.Label(self, text="Força Fy [kN]").grid(row=2, column=0, sticky="e")
        self.fy_entry = ttk.Entry(self)
        self.fy_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.fy_entry.insert(0, "0.0")

        tk.Label(self, text="Força Fz [kN] (tração positiva)").grid(row=3, column=0, sticky="e")
        self.fz_entry = ttk.Entry(self)
        self.fz_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.fz_entry.insert(0, "0.0")

        tk.Label(self, text="Ponto de aplicação X [mm]").grid(row=4, column=0, sticky="e")
        self.x_entry = ttk.Entry(self)
        self.x_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.x_entry.insert(0, "0.0")

        tk.Label(self, text="Ponto de aplicação Y [mm]").grid(row=5, column=0, sticky="e")
        self.y_entry = ttk.Entry(self)
        self.y_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        self.y_entry.insert(0, "0.0")

        tk.Label(self, text="Ponto de aplicação Z [mm]").grid(row=6, column=0, sticky="e")
        self.z_entry = ttk.Entry(self)
        self.z_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        self.z_entry.insert(0, "0.0")

        self.prefill_existing_load()

        button_frame = tk.Frame(self)
        button_frame.grid(row=7, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Confirmar", command=self.confirm).pack(side="left", padx=5)
        tk.Button(button_frame, text="Voltar", command=self.controller.show_bolt_properties).pack(side="left", padx=5)

        self.columnconfigure(1, weight=1)

    def prefill_existing_load(self):
        existing_load = getattr(self.controller, 'load', None)
        if isinstance(existing_load, VectorLoad):
            self.fx_entry.delete(0, tk.END)
            self.fx_entry.insert(0, f"{existing_load.Fx / 1000:.3f}")
            self.fy_entry.delete(0, tk.END)
            self.fy_entry.insert(0, f"{existing_load.Fy / 1000:.3f}")
            self.fz_entry.delete(0, tk.END)
            self.fz_entry.insert(0, f"{existing_load.Fz / 1000:.3f}")
            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, f"{existing_load.x:.3f}")
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, f"{existing_load.y:.3f}")
            self.z_entry.delete(0, tk.END)
            self.z_entry.insert(0, f"{existing_load.z:.3f}")

    def confirm(self):
        try:
            fx = float(self.fx_entry.get()) * 1000.0
            fy = float(self.fy_entry.get()) * 1000.0
            fz = float(self.fz_entry.get()) * 1000.0
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Todos os campos devem ser numéricos")
            return

        load = VectorLoad(fx, fy, fz, x, y, z)
        self.controller.set_load(load)
