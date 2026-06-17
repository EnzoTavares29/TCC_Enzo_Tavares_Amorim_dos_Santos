import tkinter as tk
from tkinter import ttk, messagebox
from models.bolt_properties import BoltProperties
from models.iso_bolt_table import ISO_BOLT_TABLE


class BoltPropertiesView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # Mappings for series translation
        self.series_to_display = {"coarse": "grossa", "fine": "fina"}
        self.display_to_series = {v: k for k, v in self.series_to_display.items()}

        tk.Label(self, text="Propriedades do Parafuso", font=("Arial", 14, "bold")).pack(pady=10)

        # Get available diameters from ISO_BOLT_TABLE, sorted numerically
        diameters = sorted(ISO_BOLT_TABLE.keys(), key=lambda x: float(x[1:]))

        # Diameter
        tk.Label(self, text="Diâmetro [mm]").pack(anchor="w")
        self.diameter_var = tk.StringVar(value=diameters[0] if diameters else "M6")
        self.diameter_cb = ttk.Combobox(self, textvariable=self.diameter_var, values=diameters, state="readonly")
        self.diameter_cb.pack(fill="x", padx=10, pady=4)
        self.diameter_cb.bind("<<ComboboxSelected>>", lambda e: self.update_series())

        # Series
        tk.Label(self, text="Série de Rosca").pack(anchor="w")
        self.series_var = tk.StringVar()
        self.series_cb = ttk.Combobox(self, textvariable=self.series_var, state="readonly")
        self.series_cb.pack(fill="x", padx=10, pady=4)
        self.series_cb.bind("<<ComboboxSelected>>", lambda e: None)

        # Bolt class
        tk.Label(self, text="Classe do Parafuso").pack(anchor="w")
        self.class_var = tk.StringVar(value="8.8")
        self.class_cb = ttk.Combobox(
            self, textvariable=self.class_var,
            values=["5.8", "8.8", "10.9", "12.9"],
            state="readonly"
        )
        self.class_cb.pack(fill="x", padx=10, pady=4)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="Confirmar", command=self.confirm).pack(side="left", padx=5)
        tk.Button(button_frame, text="Ver características", command=self.show_characteristics).pack(side="left", padx=5)
        tk.Button(button_frame, text="Voltar", command=self.back).pack(side="left", padx=5)

        # Initialize series options
        self.update_series()

    def update_series(self):
        diameter = self.diameter_var.get()
        if diameter in ISO_BOLT_TABLE:
            series_options = [self.series_to_display.get(s, s) for s in ISO_BOLT_TABLE[diameter].keys()]
            self.series_cb.config(values=series_options)
            if series_options:
                self.series_var.set(series_options[0])
        else:
            self.series_cb.config(values=[])

    def confirm(self):
        try:
            diameter = self.diameter_var.get()
            series_display = self.series_var.get()
            series = self.display_to_series.get(series_display, series_display)
            bolt_class = self.class_var.get()

            if not diameter or not series_display:
                messagebox.showerror("Erro", "Selecione diâmetro e série")
                return

            bp = BoltProperties(diameter, series, bolt_class)
            self.controller.set_bolt_properties(diameter, series, bolt_class)
            # navigate according to controller.return_to if set
            if getattr(self.controller, 'return_to', None) == 'dimensioning':
                # clear flag and return to dimensioning
                self.controller.return_to = None
                self.controller.go_to_dimensioning()
            else:
                self.controller.go_to_load_definition()

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def back(self):
        self.controller.show_bolt_layout()

    def show_characteristics(self):
        """Display bolt resistance characteristics in a modal"""
        try:
            diameter = self.diameter_var.get()
            series_display = self.series_var.get()
            series = self.display_to_series.get(series_display, series_display)
            bolt_class = self.class_var.get()
            if not diameter or not series_display:
                messagebox.showerror("Erro", "Selecione diâmetro e série")
                return

            bp = BoltProperties(diameter, series, bolt_class)
            msg = (
                f"Características do parafuso:\n\n"
                f"Diâmetro nominal: {bp.nominal_diameter} mm\n"
                f"Área de tração At: {bp.area_tracao:.2f} mm²\n"
                f"Limite de escoamento Sy: {bp.sy} MPa\n"
                f"Resistência última Su: {bp.su} MPa\n"
                f"Tensão de cisalhamento admissível (τadm ≈ 0.577·Sy): {bp.tau_adm:.1f} MPa\n"
            )
            messagebox.showinfo("Características do Parafuso", msg)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
