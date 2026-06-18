from models.bolt_properties import BoltProperties
from loads.vector_load import VectorLoad
from models.bolt import Bolt
from models.bolt_group import BoltGroup
import math

# Setup similar to test
scale = 25.4
bolt_positions_in = [(2.5, 1.0), (3.5, 4.0), (1.5, 4.0)]

bolt_group = BoltGroup()
bolt_group.configure(3, 381.0, 127.0)
for index, (x_in, y_in) in enumerate(bolt_positions_in):
    x_mm = x_in * scale
    y_mm = y_in * scale
    bolt_group.add_bolt(Bolt(x_mm, y_mm, f"B{index+1}"))

ct = (bolt_group.bolts[0].x, bolt_group.bolts[0].y)  # dummy centroid
load = VectorLoad(Fx=0.0, Fy=-13400.0, Fz=0.0, x=15.0*scale, y=5.0*scale, z=10.0*scale)

bolt_props = BoltProperties("M16", "coarse", "8.8")

# reproduce shear magnitude and manual calc
shear_magnitude = math.hypot(load.Fx, load.Fy)
n = len(bolt_group.bolts)
mu = 0.4
fs_target = 1.3
K = 0.2

d = bolt_props.nominal_diameter  # likely 16 (mm)

Fp_est = shear_magnitude * (fs_target/(mu * n))
t_est = K * Fp_est * d

print(f"shear_magnitude = {shear_magnitude}")
print(f"n = {n}")
print(f"mu = {mu}")
print(f"fs_target = {fs_target}")
print(f"Fp_est (N) = {Fp_est}")
print(f"d (nominal_diameter) = {d} (units: ? expected mm)")
print(f"t_est (N·mm) = {t_est}")
print(f"t_est (N·m) = {t_est/1000.0}")

# Now call vector calculation
from calculations.vector_load import VectorLoadCalculator

# debug output separator
print('\n--- debug torque reproduction ---')
calc = VectorLoadCalculator(bolt_group.bolts, load, (0,0), bolt_props, 1000.0, mu)
torque_nmm, fsj, fsb, viable = calc.optimal_torque_for_fs_target(fs_target=fs_target)
print('from class:', torque_nmm, torque_nmm/1000.0, fsj, fsb, viable)
