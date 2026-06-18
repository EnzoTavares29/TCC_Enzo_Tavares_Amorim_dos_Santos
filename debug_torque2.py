from models.bolt_properties import BoltProperties
from loads.vector_load import VectorLoad
from models.bolt import Bolt
from models.bolt_group import BoltGroup
from models.centroid import centroid
from calculations.vector_load import VectorLoadCalculator
import math

# Setup: COEMI example (3 bolts, M16 8.8, 13400 N shear)
scale = 25.4
bolt_positions_in = [(2.5, 1.0), (3.5, 4.0), (1.5, 4.0)]

bolt_group = BoltGroup()
bolt_group.configure(3, 381.0, 127.0)
for index, (x_in, y_in) in enumerate(bolt_positions_in):
    bolt_group.add_bolt(Bolt(x_in * scale, y_in * scale, f"B{index+1}"))

ct = centroid(bolt_group.bolts)
print(f"Centroid: {ct}")

load = VectorLoad(Fx=0.0, Fy=-13400.0, Fz=0.0,
                  x=15.0*scale, y=5.0*scale, z=10.0*scale)

bolt_props = BoltProperties("M16", "coarse", "8.8")
mu = 0.4
K = 0.2

print(f"\nBolt: M{bolt_props.nominal_diameter} | d={bolt_props.nominal_diameter} mm | At={bolt_props.area_tracao} mm^2 | Sy={bolt_props.sy} MPa")

# Manual estimation
shear_magnitude = math.hypot(load.Fx, load.Fy)
n = len(bolt_group.bolts)
fs_target = 1.3
Fp_est = shear_magnitude * (fs_target / (mu * n))
t_est_Nmm = K * Fp_est * bolt_props.nominal_diameter
print(f"\nManual estimate (simple, ignores eccentricity):")
print(f"  shear_magnitude = {shear_magnitude:.1f} N")
print(f"  Fp_est per bolt = {Fp_est:.1f} N")
print(f"  T_est = {t_est_Nmm:.1f} N.mm = {t_est_Nmm/1000:.3f} N.m")

# Actual calculation via class
calc = VectorLoadCalculator(bolt_group.bolts, load, ct, bolt_props, 1000.0, mu)
torque_nmm, fsj, fsb, viable = calc.optimal_torque_for_fs_target(fs_target=fs_target)
print(f"\noptimal_torque_for_fs_target(1.3):")
print(f"  Torque = {torque_nmm:.1f} N.mm = {torque_nmm/1000:.3f} N.m")
print(f"  fs_joint = {fsj:.4f}")
print(f"  fs_bolt_min = {fsb:.4f}")
print(f"  viable = {viable}")

# Verify with full calculation
calc_final = VectorLoadCalculator(bolt_group.bolts, load, ct, bolt_props, torque_nmm, mu)
result = calc_final.calculate()
print(f"\nVerification at T={torque_nmm/1000:.3f} N.m:")
print(f"  fs_joint (min per bolt) = {result['fs_joint']:.4f}")
print(f"  fs_bolt_min = {result['fs_bolt_min']:.4f}")
for b in result['per_bolt']:
    fs_a = (mu*b['Fp']/b['Fxy']) if b.get('Fxy', 0)>0 else float('inf')
    print(f"  {b['label']}: Fp={b['Fp']:.1f} N  Fxy={b['Fxy']:.1f} N  fs_atrito={fs_a:.3f}")

# Also check Cenario A torque (50% Sy*At)
Fp_bearing = 0.5 * bolt_props.sy * bolt_props.area_tracao
T_bearing_Nmm = 0.20 * Fp_bearing * bolt_props.nominal_diameter
print(f"\nCenario A (50% Sy.At): T = {T_bearing_Nmm:.1f} N.mm = {T_bearing_Nmm/1000:.3f} N.m")
calc_bearing = VectorLoadCalculator(bolt_group.bolts, load, ct, bolt_props, T_bearing_Nmm, mu)
rb = calc_bearing.calculate()
print(f"  fs_bolt_min = {rb['fs_bolt_min']:.3f}  fs_joint = {rb['fs_joint']:.3f}")
