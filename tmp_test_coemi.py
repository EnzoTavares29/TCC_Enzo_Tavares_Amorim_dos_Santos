from models.bolt import Bolt
from models.bolt_properties import BoltProperties
from models.centroid import centroid
from loads.vector_load import VectorLoad
from calculations.vector_load import VectorLoadCalculator

# Bolt layout (from your image)
bolts = [
    Bolt(25.0,25.0,'B1'),
    Bolt(50.0,50.0,'B2'),
    Bolt(10.0,70.0,'B3'),
    Bolt(78.0,82.0,'B4'),
    Bolt(20.0,82.0,'B5'),
]

cent = centroid(bolts)

bolt_props = BoltProperties('M10','coarse','8.8')

# Load from your message
load = VectorLoad(Fx=20000.0, Fy=30000.0, Fz=10000.0, x=65.0, y=45.0, z=100.0)

# user torque from your output: 439.040 N·m -> in N·mm
user_torque_Nmm = 439.040 * 1000.0

# mu assumed from UI; pick 0.2 as typical
mu = 0.2

calc = VectorLoadCalculator(bolts, load, cent, bolt_props, user_torque_Nmm, mu)
res = calc.calculate()
print('User torque FS_joint:', res['fs_joint'])

T_opt = calc.optimal_torque()
print('Optimal COEMI torque (N·mm):', T_opt)
print('Optimal COEMI torque (N·m):', T_opt/1000.0)

# show fs at that torque
calc2 = VectorLoadCalculator(bolts, load, cent, bolt_props, T_opt, mu)
res2 = calc2.calculate()
print('FS_joint at optimal torque:', res2['fs_joint'])
print('FS_bolt_min at optimal torque:', res2['fs_bolt_min'])

# If FS_joint < 1, show adjusted torque found
if res2['fs_joint'] < 1.0:
    print('COEMI FS joint < 1 -> torque adjusted to ensure FS>=1')
else:
    print('COEMI FS joint >= 1')

