import math

from calculations.preload import PreloadCalculator
from calculations.combined_stress import CombinedStressCalculator
from calculations.joint_friction import JointFrictionCalculator


class VectorLoadCalculator:
    """Unified vector-based bolt load calculator."""

    def __init__(self, bolts, load, centroid, bolt_props, torque_Nmm, mu, K=0.20):
        self.bolts = bolts
        self.load = load
        self.cx, self.cy = centroid
        self.bolt_props = bolt_props
        self.At = bolt_props.area_tracao
        self.sy = bolt_props.sy
        self.d = bolt_props.nominal_diameter
        self.torque = torque_Nmm
        self.mu = mu
        self.K = K

    def calculate(self):
        n = len(self.bolts)
        if n == 0:
            raise ValueError("Nenhum parafuso definido")

        Fx_direct = self.load.Fx / n
        Fy_direct = self.load.Fy / n
        Fz_direct = self.load.Fz / n

        rx = self.load.x - self.cx
        ry = self.load.y - self.cy
        rz = self.load.z

        moment_x = ry * self.load.Fz - rz * self.load.Fy
        moment_y = rz * self.load.Fx - rx * self.load.Fz
        moment_z = rx * self.load.Fy - ry * self.load.Fx

        sum_r2 = sum((b.x - self.cx) ** 2 + (b.y - self.cy) ** 2 for b in self.bolts)
        x_mm = [abs(b.x) for b in self.bolts]
        y_mm = [abs(b.y) for b in self.bolts]
        sum_x2_abs = sum(x * x for x in x_mm)
        sum_y2_abs = sum(y * y for y in y_mm)

        if sum_r2 == 0.0:
            raise ValueError("Geometria inválida: somatório de r² = 0")

        Fi = PreloadCalculator(self.torque, self.d, self.K).preload_force()
        if Fi < 0:
            raise ValueError("Torque de aperto inválido; verifique o valor inserido.")

        per_bolt = []
        fs_bolt_min = float("inf")
        critical = None
        active_preloads = []

        for i, b in enumerate(self.bolts):
            dx = b.x - self.cx
            dy = b.y - self.cy
            r2 = dx * dx + dy * dy
            r = math.sqrt(r2)

            if r > 0.0:
                perp_x = -dy / r
                perp_y = dx / r
            else:
                perp_x = 0.0
                perp_y = 0.0

            moment_shear = moment_z * r / sum_r2
            shear_x = Fx_direct + moment_shear * perp_x
            shear_y = Fy_direct + moment_shear * perp_y
            shear_total = math.hypot(shear_x, shear_y)

            axial_from_Mx = (moment_x * y_mm[i] / sum_y2_abs) if sum_y2_abs > 0 else 0.0
            axial_from_My = (-moment_y * x_mm[i] / sum_x2_abs) if sum_x2_abs > 0 else 0.0
            axial_moment = axial_from_Mx + axial_from_My
            axial_total = Fz_direct + axial_moment

            bolt_axial_force = Fi + axial_total
            separated = bolt_axial_force <= 0.0
            effective_preload = max(bolt_axial_force, 0.0)

            if separated:
                sigma_eq = 0.0
                fs_bolt = 0.0
            else:
                sigma_eq = CombinedStressCalculator(effective_preload, shear_total, self.At).equivalent_stress()
                fs_bolt = self.sy / sigma_eq if sigma_eq > 0.0 else float("inf")
                active_preloads.append(effective_preload)

            per_bolt.append({
                "label": b.label,
                "Fx": shear_x,
                "Fy": shear_y,
                "Fxy": shear_total,
                "Fz_direct": Fz_direct,
                "Fz_moment": axial_moment,
                "Fz": axial_total,
                "Fi": Fi,
                "Fp": effective_preload,
                "Pf_coemi_N": axial_moment,
                "sigma_eq": sigma_eq,
                "fs_bolt": fs_bolt,
                "separated": separated,
            })

            if not separated and fs_bolt < fs_bolt_min:
                fs_bolt_min = fs_bolt
                critical = b.label

        shear_magnitude = math.hypot(self.load.Fx, self.load.Fy)
        fs_joint = JointFrictionCalculator(active_preloads, self.mu, shear_magnitude).safety_factor()

        return {
            "per_bolt": per_bolt,
            "critical_bolt": critical or "Todos",
            "fs_bolt_min": fs_bolt_min if fs_bolt_min != float("inf") else 0.0,
            "fs_joint": fs_joint,
            "T_user_Nm": self.torque / 1000.0,
            "T_user_Nmm": self.torque,
            "load_value": shear_magnitude,
            "moment_vector": (moment_x, moment_y, moment_z),
            "Fp": Fi,
        }

    def optimal_torque(self):
        shear_magnitude = math.hypot(self.load.Fx, self.load.Fy)
        n = len(self.bolts)
        if shear_magnitude <= 0 or n == 0 or self.mu <= 0:
            return 0.0

        # Initial COEMI estimate based on average preload
        Fp_est = shear_magnitude / (self.mu * n)
        t_est = self.K * Fp_est * self.d

        # Helper to compute fs_joint for a given torque (N·mm)
        def fs_joint_for(torque_val):
            calc = VectorLoadCalculator(
                self.bolts,
                self.load,
                (self.cx, self.cy),
                self.bolt_props,
                torque_val,
                self.mu,
                self.K,
            )
            res = calc.calculate()
            return res.get('fs_joint', 0.0)

        # If estimated torque already gives FS >= 1, return it
        try:
            if fs_joint_for(t_est) >= 1.0:
                return t_est
        except Exception:
            # fall through to iterative search
            pass

        # Find an upper bound where FS >= 1 by exponential search
        low = max(0.0, t_est)
        high = max(low * 2.0, 1.0)
        for _ in range(40):
            try:
                if fs_joint_for(high) >= 1.0:
                    break
            except Exception:
                pass
            high *= 2.0

        # Binary search for minimal torque that yields fs_joint >= 1
        target = 1.0
        best = high
        for _ in range(40):
            mid = (low + high) / 2.0
            try:
                fsmid = fs_joint_for(mid)
            except Exception:
                fsmid = 0.0
            if fsmid >= target:
                best = mid
                high = mid
            else:
                low = mid

        return best
