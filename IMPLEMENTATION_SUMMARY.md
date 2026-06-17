# Junta Parafusada - Implementation Summary

## ✓ Completed Implementation

### 1. **Dual-Method Dimensioning System**
- **Method 1 (Shigley)**: Von Mises combined stress analysis
  - Calculates parafuso safety factor (FS_parafuso = Sy / σeq)
  - Calculates joint safety factor (FS_junta = μ × Σ Fp / F)
  - Uses user-provided torque

- **Method 2 (COEMI)**: Friction-based dimensioning
  - Calculates optimal torque: T_opt = F / (0.20 × μ × n_bolts)
  - Re-runs calculation with optimal torque
  - Joint FS optimized to ~1.0
  - Compares parafuso and joint safety factors

### 2. **Workflow Screens**

#### Screen 1: Joint Setup
- Input: number of bolts, joint width, joint height
- Dimensions the joint outline

#### Screen 2: Bolt Layout
- Add bolts with (x, y) coordinates
- Visual canvas with coordinate axes
- Boundary validation: rejects bolts outside [0, width] × [0, height]
- Centroid calculation
- Remove individual bolts or clear all

#### Screen 3: Bolt Properties Selection
- Dropdown for ISO diameter (M6, M8, M10, etc.)
- Series selection (fine/coarse)
- Bolt class selection (4.6, 5.8, 8.8, etc.)

#### Screen 4: Load Definition
- **Centered Load**: Single force P applied at centroid
- **In-Plane Eccentric**: Force P with moment M_z (eccentric in plane)
- **Out-of-Plane Eccentric**: Force P with distances L and a

#### Screen 5: Dimensioning Results
- **Torque Comparison**:
  - User-provided torque vs. COEMI optimal
  - Recommendation: use maximum of both
  
- **Method 1 Results** (Shigley with user torque):
  - Critical bolt identification
  - Minimum parafuso SF
  - Joint friction SF (μ × Σ Fp / F)
  - Critical SF = min(FS_parafuso, FS_junta)
  
- **Method 2 Results** (COEMI with optimal torque):
  - Re-calculated with optimal torque
  - Both parafuso and joint SFs
  - Expected: FS_junta ≈ 1.0
  
- **Per-Bolt Details** (with user torque):
  - Label, Safety Factor, Preload, Equivalent Stress
  - Separation status indicator
  
- **Final Recommendation**:
  - Compares critical SF from both methods
  - Advisories based on viability

### 3. **Explanation Buttons**

#### Torque Formula Button (?)
Shows the preload and torque formula:
- Preload: Fp = 0.7 × Sy × At
- Torque: T = 0.20 × Fp × d (standard 20% coefficient)
- Joint friction FS: FS_junta = (μ × Σ Fp) / F

#### Results Explanation Button (? Explicar Resultados)
Details on calculation methodology:
- **Shigley Method**: Von Mises combined stress for parafuso + friction FS for joint
- **COEMI Method**: Optimal torque that maximizes friction capacity
- Interpretation of both safety factors
- Decision criteria (both methods must have FS ≥ 1.0)

### 4. **Key Calculations Implemented**

**Preload (Shigley Formula)**:
```
Fp = 0.7 × Sy × At
T = 0.20 × Fp × d (where d is nominal diameter in mm)
```

**Von Mises Equivalent Stress**:
```
σeq = √(σ_normal² + 3 × τ_shear²)
FS_parafuso = Sy / σeq
```

**Joint Friction Safety Factor**:
```
FS_junta = (μ × Σ Fp) / F_applied
```

**Optimal COEMI Torque**:
```
T_optimal = F / (0.20 × μ × n_bolts × n_interfaces)
```

### 5. **Validation Features**

✓ **Boundary Validation**: Bolts outside [0, width] × [0, height] are rejected  
✓ **State Guards**: Null checks prevent crashes when transitioning screens  
✓ **Centroid Auto-calculation**: Called when bolt layout is finalized  
✓ **Preload/Shear Storage**: Bolts store Pf and Vb attributes during calculation  

### 6. **Files Modified**

- `controllers/app_controller.py` - Fixed `calculate_centroid()` to store tuple
- `views/dimensioning_view.py` - Complete redesign with dual-method display
- `views/bolt_layout_view.py` - Boundary validation in `add()`
- `views/joint_canvas.py` - Axes alignment and rendering

### 7. **Test Results**

```
[OK] Centroid is tuple: (30.0, 23.33)
[OK] Bolts after out-of-bounds test: 3 (rejected 1 invalid)
[OK] Both methods in results
[OK] Workflow complete
[OK] Torque suggested: 182.1 N·mm
[OK] Full results generated (1912+ chars)
```

## Ready for Local Testing

**To test the complete workflow:**

```bash
python main.py
```

**Typical Flow:**
1. Joint Setup: 3 bolts, 100×100 mm joint
2. Bolt Layout: Add 3 bolts inside bounds, try 1 out-of-bounds (rejected)
3. Bolt Properties: Select M8, ISO-4.6 (or your choice)
4. Load Definition: 1000 N centered load
5. Dimensioning: Click "Sugerir torque" → view suggestions
6. Results: See dual-method comparison with both torques and SFs
7. Explanation: Click "?" buttons to see formulas

## Known Limitations

- Units: Torque in N·mm, stress in MPa (currently inconsistent mixing)
- No unit validation on load/geometry inputs
- No save/load project functionality
- Limited error messages for invalid input

## Next Steps (Optional)

1. **Unit Normalization**: Standardize all calculations to consistent units
2. **Unit Tests**: Create pytest tests for all calculators
3. **Documentation**: Write detailed methodology README
4. **Input Validation**: Add better error handling for edge cases
5. **Export Results**: Add PDF/CSV export functionality

