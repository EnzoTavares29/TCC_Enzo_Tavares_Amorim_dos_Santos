import tkinter as tk


class JointCanvas(tk.Canvas):
    def __init__(self, master, joint_width, joint_height,
                 width=700, height=450, margin=50):
        super().__init__(master, width=width, height=height, bg="white")

        self.joint_width = float(joint_width)
        self.joint_height = float(joint_height)

        self.w = width
        self.h = height
        self.margin = margin

        # área útil do canvas
        # compute scale to fit the joint into canvas
        self.scale = min(
            (self.w - 2 * self.margin) / self.joint_width,
            (self.h - 2 * self.margin) / self.joint_height
        )

        # actual drawn joint size in pixels
        self.draw_w = self.joint_width * self.scale
        self.draw_h = self.joint_height * self.scale

        # center the joint drawing area within canvas
        self.origin_x = (self.w - self.draw_w) / 2.0
        # origin_y is the pixel y-coordinate of the world y=0 (bottom of joint)
        self.origin_y = (self.h + self.draw_h) / 2.0

        self.bolts_drawn = {}
        self.centroid_index = 0

        self.draw_base()

    # ================= COORDENADAS =================

    def world_to_canvas(self, x, y):
        cx = self.origin_x + x * self.scale
        cy = self.origin_y - y * self.scale
        return cx, cy

    # ================= DESENHO BASE =================

    def draw_base(self):
        self.delete("all")
        self.draw_joint_outline()
        self.draw_axes()

    def draw_joint_outline(self):
        x0, y0 = self.world_to_canvas(0, 0)
        x1, y1 = self.world_to_canvas(self.joint_width, self.joint_height)

        self.create_rectangle(
            x0, y1, x1, y0,
            outline="black", width=2
        )

    def draw_axes(self):
        step = 50

        # eixo X (bottom)
        for x in range(0, int(self.joint_width) + 1, step):
            px, py = self.world_to_canvas(x, 0)
            self.create_line(px, py, px, py + 5)  # tick mark
            self.create_text(px, py + 12, text=f"{x}", font=("Arial", 7), anchor="n")

        # eixo Y (left)
        for y in range(0, int(self.joint_height) + 1, step):
            px, py = self.world_to_canvas(0, y)
            self.create_line(px - 5, py, px, py)  # tick mark
            self.create_text(px - 10, py, text=f"{y}", font=("Arial", 7), anchor="e")

        # Axis labels (close to origin)
        # axis labels (near edges of the drawn joint)
        self.create_text(
            self.origin_x + self.draw_w - 20,
            self.origin_y + 18,
            text="X [mm]",
            font=("Arial", 9, "bold"),
            anchor="se"
        )
        self.create_text(
            self.origin_x + 10,
            self.origin_y - self.draw_h + 20,
            text="Y [mm]",
            font=("Arial", 9, "bold"),
            anchor="nw"
        )

    # ================= PARAFUSOS =================

    def draw_bolt(self, bolt):
        x, y = self.world_to_canvas(bolt.x, bolt.y)
        r = 6

        self.bolts_drawn[bolt.label] = (
            self.create_oval(x-r, y-r, x+r, y+r, fill="red"),
            self.create_text(x+10, y-12, text=bolt.label,
                             anchor="nw", font=("Arial", 9, "bold")),
            self.create_text(x+10, y+4,
                             text=f"({bolt.x:.1f},{bolt.y:.1f})",
                             anchor="nw", font=("Arial", 7), fill="gray")
        )

    def remove_bolt(self, label):
        for item in self.bolts_drawn[label]:
            self.delete(item)
        del self.bolts_drawn[label]

    # ================= CENTROIDE =================

    def draw_centroid(self, x_mm, y_mm):
        self.delete("centroid")
        self.centroid_index += 1
        x, y = self.world_to_canvas(x_mm, y_mm)

        self.create_line(x-8, y, x+8, y, width=2, tag="centroid")
        self.create_line(x, y-8, x, y+8, width=2, tag="centroid")

        dx, dy = 30, -30
        self.create_line(x, y, x+dx, y+dy, dash=(3, 2), tag="centroid")

        self.create_text(
            x+dx, y+dy-10,
            text=f"G{self.centroid_index}",
            font=("Arial", 10, "bold"),
            anchor="s",
            tag="centroid"
        )

        self.create_text(
            x+dx, y+dy+5,
            text=f"({x_mm:.2f} , {y_mm:.2f})",
            font=("Arial", 7),
            fill="gray",
            anchor="n",
            tag="centroid"
        )
