import tkinter as tk
from tkinter import messagebox
from models.bolt import Bolt


class BoltInputView(tk.Frame):
    def __init__(self, master, controller, canvas):
        super().__init__(master)
        self.controller = controller
        self.canvas = canvas

        self.status = tk.Label(self, font=("Arial", 10, "bold"))
        self.status.pack()

        form = tk.Frame(self)
        form.pack()

        tk.Label(form, text="x [mm]").grid(row=0, column=0)
        tk.Label(form, text="y [mm]").grid(row=1, column=0)

        self.xe = tk.Entry(form, width=8)
        self.ye = tk.Entry(form, width=8)
        self.xe.grid(row=0, column=1)
        self.ye.grid(row=1, column=1)

        tk.Button(self, text="Adicionar", command=self.add).pack(pady=4)

        self.listbox = tk.Listbox(self, height=5)
        self.listbox.pack()

        tk.Button(self, text="Remover selecionado",
                  command=self.remove).pack()

        tk.Button(self, text="Remover todos",
              command=self.remove_all).pack(pady=2)

        tk.Button(self, text="Calcular Centroide",
                  command=self.centroid).pack(pady=4)

        self.advance_btn = tk.Button(self, text="Avançar",
                                     command=self.advance, state="disabled")
        self.advance_btn.pack(pady=4)

        tk.Button(self, text="Voltar",
                  command=self.back).pack()

        self.update_status()

    def update_status(self):
        self.status.config(
            text=f"Parafusos: {self.controller.current_bolt}/"
                 f"{self.controller.expected_bolts}"
        )
        self.advance_btn.config(
            state="normal" if
            self.controller.current_bolt == self.controller.expected_bolts
            else "disabled"
        )

    def add(self):
        if self.controller.current_bolt >= self.controller.expected_bolts:
            messagebox.showwarning("Limite", "Número máximo atingido")
            return
        try:
            bolt = Bolt(float(self.xe.get()),
                        float(self.ye.get()),
                        f"B{self.controller.current_bolt+1}")
            self.controller.add_bolt(bolt)
            self.canvas.draw_bolt(bolt)
            self.listbox.insert(tk.END, bolt.label)
            self.update_status()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def remove(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        label = self.listbox.get(sel[0])
        self.controller.remove_bolt(label)
        self.canvas.remove_bolt(label)
        self.listbox.delete(sel[0])
        self.update_status()

    def remove_all(self):
        if messagebox.askyesno("Confirmar", "Remover todos os parafusos?"):
            # clear model
            self.controller.remove_all_bolts()
            # clear canvas drawings
            for i in range(self.listbox.size()):
                label = self.listbox.get(0)
                try:
                    self.canvas.remove_bolt(label)
                except Exception:
                    pass
                self.listbox.delete(0)
            self.update_status()

    def centroid(self):
        try:
            x, y = self.controller.calculate_centroid()
            self.canvas.draw_centroid(x, y)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def advance(self):
        self.controller.go_to_load_definition()

    def back(self):
        self.controller.back_to_setup()
