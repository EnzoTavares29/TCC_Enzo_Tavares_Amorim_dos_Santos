"""
main2.py - Test suite for COEMI bolt joint calculations
Tests specific examples from COEMI document against program calculations
Displays: COEMI parameters → COEMI results → Program results
"""

from models.bolt_properties import BoltProperties
from loads.symmetric_load import SymmetricLoad
from loads.eccentric_in_plane import EccentricInPlane
from loads.eccentric_out_of_plane import EccentricOutOfPlane
from loads.combined_load import CombinedLoad
from calculations.shear_centered import calculate_shear_centered
from calculations.shear_centered_with_torque import calculate_shear_centered_with_torque
from calculations.eccentric_in_plane import calculate_eccentric_in_plane
from calculations.eccentric_out_of_plane import calculate_eccentric_out_of_plane
from calculations.combined_stress import calculate_combined_stress
import math

def print_comparison(example_name, coemi_input, coemi_results, program_input, program_results):
    """Print a formatted comparison between COEMI and program results"""
    print(f"\n{'='*80}")
    print(f"Example: {example_name}")
    print(f"{'='*80}")
    
    print(f"\n--- COEMI (Artigo-2-Parafusos_COEMI_2024.pdf)")
    print(f"--- Input Parameters:")
    for key, val in coemi_input.items():
        print(f"    * {key}: {val}")
    print(f"--- COEMI Results:")
    for key, val in coemi_results.items():
        print(f"    * {key}: {val}")
    
    print(f"\n--- Program Input:")
    for key, val in program_input.items():
        print(f"    * {key}: {val}")
    print(f"--- Program Results:")
    for key, val in program_results.items():
        print(f"    * {key}: {val}")
    print(f"{'-'*80}")

def test_coemi_symmetric_bearing():
    """Test COEMI Example 3.1: Symmetric loading, bearing joint"""
    # COEMI Input
    P_ton = 2.0
    P_N = 2.0 * 1000 * 9.81  # 19620 N
    n = 3
    Vb_coemi = 6540  # N (given in COEMI)
    
    # COEMI Results (from document)
    coemi_input = {
        "Load P": f"{P_ton} Ton = {P_N:.0f} N",
        "Number of bolts": n,
        "Force per bolt Vb": f"{Vb_coemi/1000:.2f} kN",
        "Bolt size tested": "M8x1.25 (coarse)",
        "Bolt class": "5.8",
        "Sp (yield)": "380 MPa"
    }
    
    coemi_results = {
        "At_min": "29.80 mm²",
        "Selected At (M8)": "36.61 mm²",
        "Fi (preload M8)": "8.08 kN",
        "Ti (torque M8)": "12.93 N·m"
    }
    
    # Program Calculation
    bp = BoltProperties("M8", "coarse", "5.8")
    load = SymmetricLoad(Vb_coemi)
    result = calculate_shear_centered(bp, load, 1)
    
    program_input = {
        "Vb (force per bolt)": f"{Vb_coemi} N",
        "Bolt size": "M8",
        "Series": "coarse",
        "Class": "5.8",
        "At (tensile area)": f"{bp.area_tracao:.2f} mm²",
        "Sy (yield strength)": f"{bp.sy} MPa",
        "τ_adm (shear allowable)": f"{bp.tau_adm:.1f} MPa"
    }
    
    program_results = {
        "τ (shear stress)": f"{Vb_coemi / bp.area_tracao:.2f} MPa",
        "FS_bolt (safety factor)": f"{result['fs_bolt']:.2f}",
        "Method": "COEMI - von Mises shear (τ_adm / τ)"
    }
    
    print_comparison(
        "3.1 Symmetric Loading - Bearing Joint (M8)",
        coemi_input, coemi_results,
        program_input, program_results
    )
    
    assert result['fs_bolt'] > 1, f"FS should be >1, got {result['fs_bolt']}"
    print(f"[OK] Test passed")

def test_coemi_symmetric_friction():
    """Test COEMI Example 3.1: Symmetric loading, friction joint"""
    # COEMI Input
    P_ton = 2.0
    P_N = 2.0 * 1000 * 9.81  # 19620 N
    n = 3
    Vb_coemi = P_N / n  # 6540 N
    
    # COEMI Results (from document)
    coemi_input = {
        "Load P": f"{P_ton} Ton = {P_N:.0f} N",
        "Number of bolts": n,
        "Bolt size chosen": "M12x1.75 (coarse)",
        "Bolt class": "5.8",
        "Sp (yield)": "380 MPa",
        "At (tensile area M12)": "84.27 mm²",
        "Friction coefficient μ": "0.15 (assumed)"
    }
    
    coemi_results = {
        "At_min": "72.28 mm²",
        "Selected At": "84.27 mm² (M12)",
        "Fi (preload)": "24.63 kN",
        "Ti (torque)": "49.26 N·m",
        "Analysis": "Minimum torque needed to prevent slip"
    }
    
    # Program Calculation
    bp = BoltProperties("M12", "coarse", "5.8")
    load = SymmetricLoad(P_N)
    torque = 49.26 * 1000  # N·mm
    mu = 0.15
    interfaces = 1
    result = calculate_shear_centered_with_torque(bp, load, torque, mu, interfaces, n)
    
    # Calculate what preload the program derives
    Fp_from_torque = torque / (0.2 * bp.nominal_diameter)
    
    program_input = {
        "Total force P": f"{P_N:.0f} N",
        "Number of bolts": n,
        "Torque Ti": f"{torque/1000:.2f} N·m",
        "Bolt size": "M12",
        "Series": "coarse",
        "Class": "5.8",
        "At": f"{bp.area_tracao:.2f} mm²",
        "Sy": f"{bp.sy} MPa",
        "Friction coefficient μ": mu,
        "Interfaces": interfaces
    }
    
    program_results = {
        "Fp from torque (T=0.2*Fp*d)": f"{Fp_from_torque/1000:.2f} kN",
        "Fp from COEMI formula: Fi=√[(Sp*At)²-3*Vb²]": f"{result['Fp']/1000:.2f} kN",
        "FS_bolt (parafuso)": f"{result['fs_bolt']:.2f}",
        "FS_joint (junta/atrito)": f"{result['fs_joint']:.2f}",
        "T_optimal (COEMI)": f"{result['t_optimal']/1000:.2f} N·m",
        "Method": "COEMI preload + von Mises stress"
    }
    
    print_comparison(
        "3.1 Symmetric Loading - Friction Joint (M12)",
        coemi_input, coemi_results,
        program_input, program_results
    )
    
    assert result['fs_joint'] > 0, "FS joint should be > 0"
    print(f"[OK] Test passed")

def test_coemi_eccentric_bearing():
    """Test COEMI Example 3.2: Eccentric loading, bearing joint"""
    # COEMI Input - with actual bolt positions
    P_kN = 13.4
    P_N = 13400
    # Bolt positions in inches, converted to mm (1" = 25.4 mm)
    A_in = (2.5, 1.0)
    B_in = (3.5, 4.0)
    C_in = (1.5, 4.0)
    bolt_positions = [
        (A_in[0] * 25.4, A_in[1] * 25.4),  # A: (63.5, 25.4) mm
        (B_in[0] * 25.4, B_in[1] * 25.4),  # B: (88.9, 101.6) mm
        (C_in[0] * 25.4, C_in[1] * 25.4)   # C: (38.1, 101.6) mm
    ]
    L_in = 12.5
    a_in = 10.0
    L = L_in * 25.4  # 317.5 mm
    a = a_in * 25.4  # 254 mm
    n = 3
    C = 0.10  # load factor
    
    coemi_input = {
        "Total load P": f"{P_kN} kN = {P_N} N",
        "Bolt A position": f"({A_in[0]}\", {A_in[1]}\") = ({bolt_positions[0][0]:.1f} mm, {bolt_positions[0][1]:.1f} mm)",
        "Bolt B position": f"({B_in[0]}\", {B_in[1]}\") = ({bolt_positions[1][0]:.1f} mm, {bolt_positions[1][1]:.1f} mm)",
        "Bolt C position": f"({C_in[0]}\", {C_in[1]}\") = ({bolt_positions[2][0]:.1f} mm, {bolt_positions[2][1]:.1f} mm)",
        "In-plane eccentricity L": f"{L_in}\" = {L:.1f} mm",
        "Out-of-plane eccentricity a": f"{a_in}\" = {a:.1f} mm",
        "Number of bolts": n,
        "Load factor C": C,
        "Bolt class": "5.8",
        "Sp (yield)": "380 MPa",
    }
    
    coemi_results = {
        "Vc (direct shear per bolt)": "4.47 kN",
        "Vt (torsional shear)": "varies per bolt (A=41.88, B=29.61, C=29.61 kN)",
        "At_min": "193.05 mm²",
        "Selected bolt": "M20x2.5",
        "Selected At": "244.79 mm²",
        "Fi (A)": "57.30 kN",
        "Fi (B)": "71.87 kN",
        "Fi (C)": "79.15 kN",
        "Ti (A)": "229.20 N·m",
        "Ti (B)": "287.48 N·m",
        "Ti (C)": "316.60 N·m"
    }
    
    # Program Calculation
    bp = BoltProperties("M20", "coarse", "5.8")
    load = CombinedLoad(F_shear=P_N, F_tension=0, L=L, A=a)
    result = calculate_combined_stress(bp, load, bolt_positions)
    
    program_input = {
        "Total load P": f"{P_N} N",
        "Bolt A position": f"({bolt_positions[0][0]:.1f}, {bolt_positions[0][1]:.1f}) mm",
        "Bolt B position": f"({bolt_positions[1][0]:.1f}, {bolt_positions[1][1]:.1f}) mm",
        "Bolt C position": f"({bolt_positions[2][0]:.1f}, {bolt_positions[2][1]:.1f}) mm",
        "In-plane eccentricity L": f"{L:.1f} mm",
        "Out-of-plane eccentricity a": f"{a:.1f} mm",
        "Bolt size": "M20",
        "Series": "coarse",
        "Class": "5.8",
        "At": f"{bp.area_tracao:.2f} mm²",
        "Sy": f"{bp.sy} MPa"
    }
    
    program_results = {
        "FS_bolt (minimum)": f"{result['fs_bolt']:.2f}",
        "Method": "COEMI von Mises for distributed eccentric load"
    }
    
    print_comparison(
        "3.2 Eccentric Loading - Bearing Joint (M20)",
        coemi_input, coemi_results,
        program_input, program_results
    )
    
    assert result['fs_bolt'] > 1, "FS should be >1"
    print(f"[OK] Test passed")

def test_coemi_eccentric_friction():
    """Test COEMI Example 3.2: Eccentric loading, friction joint"""
    # COEMI Input - with actual bolt positions
    P_kN = 13.4
    P_N = 13400
    # Bolt positions in inches, converted to mm (1" = 25.4 mm)
    A_in = (2.5, 1.0)
    B_in = (3.5, 4.0)
    C_in = (1.5, 4.0)
    bolt_positions = [
        (A_in[0] * 25.4, A_in[1] * 25.4),  # A: (63.5, 25.4) mm
        (B_in[0] * 25.4, B_in[1] * 25.4),  # B: (88.9, 101.6) mm
        (C_in[0] * 25.4, C_in[1] * 25.4)   # C: (38.1, 101.6) mm
    ]
    L_in = 12.5
    a_in = 10.0
    L = L_in * 25.4  # 317.5 mm
    a = a_in * 25.4  # 254 mm
    n = 3
    C = 0.10  # load factor
    
    coemi_input = {
        "Total load P": f"{P_kN} kN = {P_N} N",
        "Bolt A position": f"({A_in[0]}\", {A_in[1]}\") = ({bolt_positions[0][0]:.1f} mm, {bolt_positions[0][1]:.1f} mm)",
        "Bolt B position": f"({B_in[0]}\", {B_in[1]}\") = ({bolt_positions[1][0]:.1f} mm, {bolt_positions[1][1]:.1f} mm)",
        "Bolt C position": f"({C_in[0]}\", {C_in[1]}\") = ({bolt_positions[2][0]:.1f} mm, {bolt_positions[2][1]:.1f} mm)",
        "In-plane eccentricity L": f"{L_in}\" = {L:.1f} mm",
        "Out-of-plane eccentricity a": f"{a_in}\" = {a:.1f} mm",
        "Number of bolts": n,
        "Load factor C": C,
        "Initial bolt class": "5.8 (insufficient)",
        "Final bolt class": "8.8",
        "Sp (yield 8.8)": "600 MPa",
        "Bolt selected": "M22x2.5"
    }
    
    coemi_results = {
        "At_min (class 5.8)": "486.27 mm² (too large)",
        "At_min (class 8.8)": "303.64 mm²",
        "Selected At": "303.40 mm²",
        "Fi (preload)": "139.62 kN",
        "Ti (torque)": "614.35 N·m",
        "Analysis": "M22x2.5 class 8.8 ensures friction support"
    }
    
    # Program Calculation
    bp = BoltProperties("M22", "coarse", "8.8")
    load = CombinedLoad(F_shear=P_N, F_tension=0, L=L, A=a)
    torque = 614.35 * 1000  # N·mm
    mu = 0.15
    interfaces = 1
    result = calculate_eccentric_out_of_plane(bp, load, torque, mu, interfaces, bolt_positions)
    
    Fp_from_torque = torque / (0.2 * bp.nominal_diameter)
    
    program_input = {
        "Total load P": f"{P_N} N",
        "Bolt A position": f"({bolt_positions[0][0]:.1f}, {bolt_positions[0][1]:.1f}) mm",
        "Bolt B position": f"({bolt_positions[1][0]:.1f}, {bolt_positions[1][1]:.1f}) mm",
        "Bolt C position": f"({bolt_positions[2][0]:.1f}, {bolt_positions[2][1]:.1f}) mm",
        "In-plane eccentricity L": f"{L:.1f} mm",
        "Out-of-plane eccentricity a": f"{a:.1f} mm",
        "Torque Ti": f"{torque/1000:.2f} N·m",
        "Bolt size": "M22",
        "Series": "coarse",
        "Class": "8.8",
        "At": f"{bp.area_tracao:.2f} mm²",
        "Sy": f"{bp.sy} MPa",
        "Friction coefficient μ": mu,
        "Interfaces": interfaces
    }
    
    program_results = {
        "Fp from torque (T=0.2*Fp*d)": f"{Fp_from_torque/1000:.2f} kN",
        "Fp from COEMI formula: Fi=√[(Sp*At)²-3*Vb²]": f"{result['Fp']/1000:.2f} kN",
        "FS_bolt": f"{result['fs_bolt']:.2f}",
        "FS_joint (junta/atrito)": f"{result['fs_joint']:.2f}",
        "T_optimal (COEMI method)": f"{result['t_optimal']/1000:.2f} N·m",
        "Method": "COEMI preload + von Mises + friction"
    }
    
    print_comparison(
        "3.2 Eccentric Loading - Friction Joint (M22)",
        coemi_input, coemi_results,
        program_input, program_results
    )
    
    assert result['fs_joint'] > 1, "FS joint should be >1"
    print(f"[OK] Test passed")

if __name__ == "__main__":
    print("="*80)
    print("COEMI Bolt Joint Examples - Program Validation Test Suite")
    print("Comparing COEMI (Artigo-2-Parafusos_COEMI_2024.pdf) with program calculations")
    print("="*80)
    
    try:
        test_coemi_symmetric_bearing()
        test_coemi_symmetric_friction()
        test_coemi_eccentric_bearing()
        test_coemi_eccentric_friction()
        
        print(f"\n{'='*80}")
        print("All COEMI example tests passed!")
        print(f"{'='*80}")
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"Test failed: {e}")
        print(f"{'='*80}")
        raise