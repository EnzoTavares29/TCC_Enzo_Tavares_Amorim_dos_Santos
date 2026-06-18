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

        # PreloadCalculator expects torque in N·mm and diameter in mm; it returns Fp in N
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
        
        # FS_junta = min(μ × Fp_i / V_i) sobre todos os parafusos ativos (COEMI)
        # Isso captura o parafuso crítico ao escorregamento, não a média da junta.
        fs_joint_min = float("inf")
        for bolt in per_bolt:
            if not bolt.get('separated', False):
                Fp_i = bolt.get('Fp', 0.0)
                V_i  = bolt.get('Fxy', 0.0)
                if V_i > 0.0 and Fp_i > 0.0:
                    fs_joint_min = min(fs_joint_min, (self.mu * Fp_i) / V_i)
        if fs_joint_min == float("inf"):
            fs_joint_min = 0.0

        return {
            "per_bolt": per_bolt,
            "critical_bolt": critical or "Todos",
            "fs_bolt_min": fs_bolt_min if fs_bolt_min != float("inf") else 0.0,
            "fs_joint": fs_joint_min,
            "T_user_Nm": self.torque / 1000.0,
            "T_user_Nmm": self.torque,
            "load_value": shear_magnitude,
            "moment_vector": (moment_x, moment_y, moment_z),
            "Fp": Fi,
        }

    def optimal_torque_for_fs_target(self, fs_target=1.3):
        """
        Encontra o torque mínimo necessário para atingir FS_junta >= fs_target.
        
        CORREÇÃO CRÍTICA: FS_junta é calculado como o FS mínimo entre todos os parafusos:
        FS_junta_i = (μ × Fp_i) / V_i    (por parafuso)
        FS_junta = min( FS_junta_i )     (parafuso crítico)
        
        Args:
            fs_target: fator de segurança alvo (padrão: 1.3 para Junta de Atrito)
        
        Returns:
            tuple: (torque_Nmm, fs_junta_obtido, fs_parafuso_minimo, viável)
        """
        n = len(self.bolts)
        if n == 0 or self.mu <= 0:
            return (0.0, 0.0, 0.0, False)

        # Helper para calcular FS_junta por parafuso
        def evaluate_torque(torque_val):
            try:
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
                
                # Calcular FS_junta como o FS mínimo entre todos os parafusos
                # FS_junta_i = (μ × Fp_i) / V_i
                fs_joint_min = float("inf")
                for bolt in res.get('per_bolt', []):
                    if not bolt.get('separated', False):
                        Fp = bolt.get('Fp', 0.0)
                        V = bolt.get('Fxy', 0.0)
                        if V > 0 and Fp > 0:
                            fs_parafuso_atrito = (self.mu * Fp) / V
                            fs_joint_min = min(fs_joint_min, fs_parafuso_atrito)
                
                if fs_joint_min == float("inf"):
                    fs_joint_min = 0.0
                
                return {
                    'fs_joint': fs_joint_min,
                    'fs_bolt_min': res.get('fs_bolt_min', 0.0),
                    'success': True
                }
            except Exception:
                return {'fs_joint': 0.0, 'fs_bolt_min': 0.0, 'success': False}

        # Exponential search para encontrar limite superior
        low = 100.0  # 100 N·mm mínimo
        high = 10000.0  # começar em 10,000 N·mm
        for _ in range(50):
            result = evaluate_torque(high)
            if result['success'] and result['fs_joint'] >= fs_target:
                break
            high *= 2.0

        # Binary search para torque mínimo com FS_junta >= fs_target
        best_torque = high
        best_fs_joint = 0.0
        best_fs_bolt = 0.0
        for iteration in range(60):
            mid = (low + high) / 2.0
            result = evaluate_torque(mid)
            
            if not result['success']:
                low = mid
                continue
            
            fs_joint_val = result['fs_joint']
            fs_bolt_val = result['fs_bolt_min']
            
            if fs_joint_val >= fs_target:
                # Atende o alvo: registrar e tentar reduzir torque
                if mid < best_torque:
                    best_torque = mid
                    best_fs_joint = fs_joint_val
                    best_fs_bolt = fs_bolt_val
                high = mid
            else:
                # Não atende: aumentar torque
                low = mid
        
        # Avaliação final
        final_result = evaluate_torque(best_torque)
        viável = (final_result['fs_joint'] >= fs_target and 
                  final_result['fs_bolt_min'] > 1.0)
        
        return (best_torque, final_result['fs_joint'], final_result['fs_bolt_min'], viável)

    def optimal_torque(self):
        """
        Legacy method: retorna torque para FS_junta >= 1.0
        (mantém compatibilidade, mas novo código deve usar optimal_torque_for_fs_target)
        """
        torque, fs_j, fs_b, _ = self.optimal_torque_for_fs_target(fs_target=1.0)
        return torque
