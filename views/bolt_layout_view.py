import tkinter as tk
from tkinter import messagebox, simpledialog
from views.joint_canvas import JointCanvas


class BoltLayoutView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        # Title
        tk.Label(self, text="Layout da Junta", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=8)

        # Left: canvas
        joint_w = getattr(controller.bolt_group, 'width', 100)
        joint_h = getattr(controller.bolt_group, 'height', 100)
        self.canvas = JointCanvas(self, joint_w, joint_h)
        self.canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Right: controls
        ctrl = tk.Frame(self)
        ctrl.grid(row=1, column=1, sticky="nw", padx=10, pady=10)

        self.status = tk.Label(ctrl, font=("Arial", 10, "bold"))
        self.status.pack(anchor="w")

        form = tk.Frame(ctrl)
        form.pack(pady=6)

        tk.Label(form, text="x [mm]").grid(row=0, column=0)
        tk.Label(form, text="y [mm]").grid(row=1, column=0)

        self.xe = tk.Entry(form, width=10)
        self.ye = tk.Entry(form, width=10)
        self.xe.grid(row=0, column=1, padx=4, pady=2)
        self.ye.grid(row=1, column=1, padx=4, pady=2)

        tk.Button(ctrl, text="Adicionar", command=self.add).pack(fill="x", pady=4)

        self.listbox = tk.Listbox(ctrl, height=8, width=24)
        self.listbox.pack(pady=6)

        tk.Button(ctrl, text="Remover selecionado", command=self.remove).pack(fill="x", pady=2)
        tk.Button(ctrl, text="Remover todos", command=self.remove_all).pack(fill="x", pady=2)

        tk.Button(ctrl, text="Calcular Centroide", command=self.centroid).pack(fill="x", pady=6)

        self.advance_btn = tk.Button(ctrl, text="Avançar", command=self.advance, state="disabled")
        self.advance_btn.pack(fill="x", pady=6)

        tk.Button(ctrl, text="Voltar", command=self.back).pack(fill="x", pady=2)

        # layout weight so canvas expands
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # populate existing bolts (if any)
        self.update_status()
        if controller.bolt_group and controller.bolt_group.bolts:
            for b in controller.bolt_group.bolts:
                self.listbox.insert(tk.END, b.label)
                self.canvas.draw_bolt(b)

    # ---------------- UI actions ----------------
    def update_status(self):
        self.status.config(text=f"Parafusos: {self.controller.current_bolt}/{self.controller.expected_bolts}")
        self.advance_btn.config(state="normal" if self.controller.current_bolt == self.controller.expected_bolts else "disabled")

    def add(self):
        if self.controller.current_bolt >= self.controller.expected_bolts:
            tk.messagebox.showwarning("Limite", "Número máximo atingido")
            return
        try:
            x = float(self.xe.get())
            y = float(self.ye.get())
        except ValueError:
            tk.messagebox.showerror("Erro", "Coordenadas inválidas")
            return
        # Validate that bolt is within joint bounds
        if x < 0 or x > self.controller.bolt_group.width or y < 0 or y > self.controller.bolt_group.height:
            messagebox.showerror(
                "Erro",
                f"Parafuso fora dos limites da junta.\n"
                f"X deve estar entre 0 e {self.controller.bolt_group.width}\n"
                f"Y deve estar entre 0 e {self.controller.bolt_group.height}"
            )
            return
        # create bolt with next label
        label = f"B{self.controller.current_bolt+1}"
        from models.bolt import Bolt
        b = Bolt(x, y, label)
        self.controller.add_bolt(b)
        self.canvas.draw_bolt(b)
        self.listbox.insert(tk.END, b.label)
        self.update_status()

    def remove(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        label = self.listbox.get(sel[0])
        self.controller.remove_bolt(label)
        try:
            self.canvas.remove_bolt(label)
        except Exception:
            pass
        self.listbox.delete(sel[0])
        self.update_status()

    def remove_all(self):
        if tk.messagebox.askyesno("Confirmar", "Remover todos os parafusos?"):
            # clear model
            self.controller.remove_all_bolts()
            # remove drawings
            for label in list(self.canvas.bolts_drawn.keys()):
                try:
                    self.canvas.remove_bolt(label)
                except Exception:
                    pass
            # clear listbox
            self.listbox.delete(0, tk.END)
            self.update_status()

    def centroid(self):
        try:
            x, y = self.controller.calculate_centroid()
            self.canvas.draw_centroid(x, y)
        except Exception as e:
            tk.messagebox.showerror("Erro", str(e))

    def advance(self):
        if self.controller.current_bolt != self.controller.expected_bolts:
            messagebox.showwarning("Aviso", "Insira todos os parafusos antes de avançar")
            return
        # finalize bolts and proceed to bolt properties selection
        try:
            self.controller.finalize_bolts(self.canvas)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def back(self):
        self.controller.back()
