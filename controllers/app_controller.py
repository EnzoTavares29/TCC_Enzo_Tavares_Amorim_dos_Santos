import tkinter as tk
from tkinter import messagebox

from views.joint_setup_view import JointSetupView
from views.bolt_layout_view import BoltLayoutView
from views.bolt_input_view import BoltInputView
from views.bolt_properties_view import BoltPropertiesView
from views.dimensioning_view import DimensioningView
from views.load_definition_view import LoadDefinitionView

from models.bolt_group import BoltGroup
from models.bolt_properties import BoltProperties
from models.centroid import centroid
from loads.vector_load import VectorLoad


class AppController:
    def __init__(self, root: tk.Tk):
        self.root = root

        # application state
        self.load_type = None
        self.load = None

        self.bolt_group = None
        self.centroid = None
        self.bolt_props = None
        self.return_to = None

        self.expected_bolts = 0
        self.current_bolt = 0
        self.current_view = None

        self.show_joint_setup()

    # ---------- Navigation ----------

    def clear_view(self):
        if self.current_view:
            self.current_view.destroy()

    def show_joint_setup(self):
        self.clear_view()
        self.load = None
        self.load_type = None
        self.current_view = JointSetupView(self.root, self)
        self.current_view.pack(fill="both", expand=True)

    def show_bolt_layout(self):
        self.clear_view()
        self.current_view = BoltLayoutView(self.root, self)
        self.current_view.pack(fill="both", expand=True)

    def show_bolt_input(self, canvas):
        self.clear_view()
        self.current_view = BoltInputView(self.root, self, canvas)
        self.current_view.pack(fill="both", expand=True)

    def show_dimensioning(self):
        self.clear_view()
        self.current_view = DimensioningView(self.root, self)
        self.current_view.pack(fill="both", expand=True)

    def show_bolt_properties(self):
        self.clear_view()
        self.current_view = BoltPropertiesView(self.root, self)
        self.current_view.pack(fill="both", expand=True)

    # ---------- Flow ----------

    def set_joint_geometry(self, n_bolts, width, height):
        self.bolt_group = BoltGroup()
        self.bolt_group.configure(n_bolts, width, height)
        self.expected_bolts = n_bolts
        self.current_bolt = 0
        self.load = None
        self.load_type = None
        self.show_bolt_layout()

    def load_tester_example(self):
        from models.bolt import Bolt

        scale = 25.4  # converter polegadas para mm
        bolt_positions_in = [
            (2.5, 1.0),
            (3.5, 4.0),
            (1.5, 4.0)
        ]
        self.bolt_group = BoltGroup()
        self.bolt_group.configure(len(bolt_positions_in), 381.0, 127.0)
        self.expected_bolts = len(bolt_positions_in)
        self.current_bolt = 0
        self.bolt_group.bolts = []

        for index, (x_in, y_in) in enumerate(bolt_positions_in):
            x_mm = x_in * scale
            y_mm = y_in * scale
            label = f"B{index + 1}"
            self.add_bolt(Bolt(x_mm, y_mm, label))

        self.centroid = centroid(self.bolt_group.bolts)

        # The COEMI example uses 10 in (254 mm) for the z offset.
        self.load = VectorLoad(
            Fx=0.0,
            Fy=-13400.0,
            Fz=0.0,
            x=15.0 * scale,
            y=5.0 * scale,
            z=10.0 * scale
        )

        self.show_bolt_layout()

    def add_bolt(self, bolt):
        # Ensure a BoltGroup exists (robustness for programmatic calls)
        if self.bolt_group is None:
            from models.bolt_group import BoltGroup
            self.bolt_group = BoltGroup()
            # fallback configuration if none provided
            self.bolt_group.configure(self.expected_bolts or 1, 100.0, 100.0)

        self.bolt_group.add_bolt(bolt)

        # update counter used by the input view
        self.current_bolt = min(self.current_bolt + 1, self.expected_bolts or self.current_bolt + 1)

    def finalize_bolts(self, canvas):
        if not self.bolt_group or not self.bolt_group.bolts:
            raise ValueError("Nenhum parafuso definido")

        self.centroid = centroid(self.bolt_group.bolts)
        self.show_bolt_properties()

    def set_bolt_properties(self, diameter, series, bolt_class):
        self.bolt_props = BoltProperties(diameter, series, bolt_class)

    # ---------- Additional navigation & helpers required by views ----------
    def go_to_load_definition(self):
        if not self.bolt_props:
            # safety: need bolt properties before load definition
            messagebox.showwarning("Aviso", "Selecione as propriedades do parafuso primeiro")
            self.show_bolt_properties()
            return

        self.clear_view()
        self.current_view = LoadDefinitionView(self.root, self)
        self.current_view.pack(fill="both", expand=True)

    def back_to_setup(self):
        self.show_joint_setup()

    def remove_bolt(self, label):
        # remove bolt by label from bolt_group
        if not self.bolt_group:
            return
        for i, b in enumerate(self.bolt_group.bolts):
            if b.label == label:
                self.bolt_group.bolts.pop(i)
                self.current_bolt = max(0, self.current_bolt - 1)
                return

    def remove_all_bolts(self):
        if not self.bolt_group:
            return
        self.bolt_group.bolts.clear()
        self.current_bolt = 0

    def calculate_centroid(self):
        if not self.bolt_group or not self.bolt_group.bolts:
            raise ValueError("Nenhum parafuso definido")
        self.centroid = centroid(self.bolt_group.bolts)
        return self.centroid

    def set_load(self, load):
        self.load = load
        self.load_type = 'vector'
        self.show_dimensioning()

    def go_to_dimensioning(self):
        self.show_dimensioning()

    def back(self):
        self.show_joint_setup()
