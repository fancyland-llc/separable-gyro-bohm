"""
GREENWALD DIAGNOSTIC
====================
Does adding a current term fix JET and JT-60U?

The hypothesis: the ε^(-5/4) term partially captures current effects 
through q ~ ε*B/I_p, but not completely. High-current machines where 
the Shafranov shift is large violate the approximation.

Test: I_p normalized by Greenwald current I_G = n_e × π × a²
"""
import numpy as np
from scipy.optimize import minimize

mu_0 = 4 * np.pi * 1e-7
m_p = 1.67e-27
e_ch = 1.602e-19
epsilon_0 = 8.854e-12
m_e = 9.109e-31

# Machine data WITH plasma current where known
# I_p in MA, from published H-mode scenarios
machines = [
    {"name":"JET",   "R":2.90,"epsilon":0.31,"kappa":1.75,"B_T":3.8, "n_e":4.1e19,"M":2.5,"tau_exp":0.89,"I_p":3.0,  "type":"tokamak"},
    {"name":"DIII-D","R":1.67,"epsilon":0.36,"kappa":1.70,"B_T":2.0, "n_e":3.5e19,"M":2.0,"tau_exp":0.14,"I_p":1.5,  "type":"tokamak"},
    {"name":"ASDEX", "R":1.65,"epsilon":0.30,"kappa":1.60,"B_T":2.5, "n_e":7.0e19,"M":2.0,"tau_exp":0.11,"I_p":0.8,  "type":"tokamak"},
    {"name":"JT-60U","R":3.40,"epsilon":0.26,"kappa":1.50,"B_T":3.7, "n_e":3.0e19,"M":2.0,"tau_exp":0.25,"I_p":2.5,  "type":"tokamak"},
    {"name":"ITER",  "R":6.20,"epsilon":0.32,"kappa":1.70,"B_T":5.3, "n_e":1.0e20,"M":2.5,"tau_exp":3.70,"I_p":15.0, "type":"tokamak"},
    {"name":"W7-X",  "R":5.50,"epsilon":0.09,"kappa":1.00,"B_T":2.5, "n_e":1.0e20,"M":2.0,"tau_exp":0.15,"I_p":0.0,  "type":"stellarator"},  # No plasma current in stellarator
    {"name":"LHD",   "R":3.90,"epsilon":0.15,"kappa":1.00,"B_T":2.75,"n_e":5.0e19,"M":2.0,"tau_exp":0.09,"I_p":0.0,  "type":"stellarator"},  # No plasma current in stellarator
]

beta = 0.025

def compute_machine_params(m):
    """Same as final_validation_v2.py"""
    R = m["R"]
    a = R * m["epsilon"]
    kappa = m["kappa"]
    B_T = m["B_T"]
    n_e = m["n_e"]
    M = m["M"]
    
    B_pressure = B_T**2 / (2 * mu_0)
    T_e_J = beta * B_pressure / n_e
    v_th = np.sqrt(T_e_J / (M * m_p))
    rho_i = M * m_p * v_th / (e_ch * B_T)
    rho_star = rho_i / a
    Omega_i = e_ch * B_T / (M * m_p)
    chi_gB = rho_i**2 * Omega_i
    tau_base = (a**2 * kappa) / chi_gB
    
    ln_Lambda = 17.0
    nu_ei = (n_e * e_ch**4 * ln_Lambda) / \
            (12 * np.pi**1.5 * epsilon_0**2 * np.sqrt(m_e) * T_e_J**1.5)
    q_approx = 1.0 / m["epsilon"]
    nu_star = nu_ei * q_approx * R / (m["epsilon"]**1.5 * v_th)
    
    return tau_base, rho_star, nu_star, m["epsilon"], a

# Compute parameters
params = [compute_machine_params(m) for m in machines]
tau_bases = np.array([p[0] for p in params])
rho_stars = np.array([p[1] for p in params])
nu_stars = np.array([p[2] for p in params])
epsilons = np.array([p[3] for p in params])
a_values = np.array([p[4] for p in params])
tau_exps = np.array([m["tau_exp"] for m in machines])
names = [m["name"] for m in machines]
types = [m["type"] for m in machines]
I_ps = np.array([m["I_p"] for m in machines])  # MA
n_es = np.array([m["n_e"] for m in machines])

# Rational exponents from theory
alpha_rat = -5/8   # ρ*
beta_rat = -2/7    # ν*
gamma_rat = -5/4   # ε

print("="*80)
print("GREENWALD DIAGNOSTIC")
print("="*80)

# ============================================================================
# STEP 1: Compute Greenwald fractions for tokamaks
# ============================================================================
print("\n" + "-"*80)
print("STEP 1: GREENWALD FRACTIONS")
print("-"*80)
print("\nGreenwald density limit: n_G = I_p / (π × a²)  [in 10²⁰ m⁻³, I_p in MA]")
print("Greenwald fraction: f_G = n_e / n_G")
print()

print(f"{'Machine':<10}{'I_p (MA)':>10}{'a (m)':>8}{'n_e (10²⁰)':>12}{'n_G (10²⁰)':>12}{'f_G':>8}")
print("-"*60)

f_greenwalds = []
for i, m in enumerate(machines):
    a = a_values[i]
    I_p = I_ps[i]
    n_e = n_es[i]
    
    if I_p > 0:
        # Greenwald limit: n_G = I_p / (π × a²) in units of 10²⁰ m⁻³ when I_p in MA
        n_G = I_p / (np.pi * a**2)  # 10²⁰ m⁻³
        f_G = (n_e / 1e20) / n_G
        f_greenwalds.append(f_G)
        print(f"{names[i]:<10}{I_p:>10.1f}{a:>8.2f}{n_e/1e20:>12.2f}{n_G:>12.2f}{f_G:>8.2f}")
    else:
        f_greenwalds.append(np.nan)
        print(f"{names[i]:<10}{'N/A':>10}{a:>8.2f}{n_e/1e20:>12.2f}{'N/A':>12}{'N/A':>8}  (stellarator)")

f_greenwalds = np.array(f_greenwalds)

# ============================================================================
# STEP 2: Compute errors with current formula (no current term)
# ============================================================================
print("\n" + "-"*80)
print("STEP 2: CURRENT FORMULA ERRORS (no current term)")
print("-"*80)

C_gemini = 3 * np.pi / np.sqrt(2)

tau_preds_base = tau_bases * C_gemini * (rho_stars**alpha_rat) * (nu_stars**beta_rat) * (epsilons**gamma_rat)
errors_base = np.abs(tau_preds_base - tau_exps) / tau_exps * 100

print(f"\nFormula: τ_E = (3π/√2) × (a²κ/χ_gB) × ρ*^(-5/8) × ν*^(-2/7) × ε^(-5/4)")
print()
print(f"{'Machine':<10}{'τ_pred':>10}{'τ_exp':>10}{'Error%':>10}{'f_G':>8}")
print("-"*48)
for i in range(len(machines)):
    f_g_str = f"{f_greenwalds[i]:.2f}" if not np.isnan(f_greenwalds[i]) else "N/A"
    print(f"{names[i]:<10}{tau_preds_base[i]:>10.4f}{tau_exps[i]:>10.4f}{errors_base[i]:>9.1f}%{f_g_str:>8}")

print(f"\nMean error: {np.mean(errors_base):.1f}%")

# ============================================================================
# STEP 3: Correlate errors with Greenwald fraction
# ============================================================================
print("\n" + "-"*80)
print("STEP 3: ERROR CORRELATION WITH GREENWALD FRACTION")
print("-"*80)

tok_mask = np.array([t == "tokamak" for t in types])
tok_errors = errors_base[tok_mask]
tok_f_g = f_greenwalds[tok_mask]
tok_names = [names[i] for i, m in enumerate(machines) if tok_mask[i]]

# Correlation
valid_mask = ~np.isnan(tok_f_g)
from scipy.stats import pearsonr, spearmanr

r_pearson, p_pearson = pearsonr(tok_errors[valid_mask], tok_f_g[valid_mask])
r_spearman, p_spearman = spearmanr(tok_errors[valid_mask], tok_f_g[valid_mask])

print(f"\nCorrelation of error with Greenwald fraction (tokamaks only):")
print(f"  Pearson r = {r_pearson:.3f} (p = {p_pearson:.4f})")
print(f"  Spearman ρ = {r_spearman:.3f} (p = {p_spearman:.4f})")

# Sign of residual (over vs underprediction)
print("\n" + "-"*40)
residuals = tau_preds_base - tau_exps  # positive = overprediction
print("Residual analysis (pred - exp):")
for i in range(len(machines)):
    if tok_mask[i]:
        sign = "OVER" if residuals[i] > 0 else "UNDER"
        print(f"  {names[i]:<10}: {residuals[i]:>+.4f}s ({sign})")

# ============================================================================
# STEP 4: Try adding a current correction term
# ============================================================================
print("\n" + "-"*80)
print("STEP 4: TRY ADDING CURRENT CORRECTION TERM")
print("-"*80)

# Hypothesis 1: τ_E ~ f_G^δ for some exponent δ
# For stellarators, f_G doesn't apply — use 1.0 as default

# Fit δ on tokamaks only, then test if stellarators still work
def compute_error_with_greenwald(C, delta, f_g_default=1.0):
    """Compute error with Greenwald correction term."""
    errors = []
    preds = []
    for i in range(len(machines)):
        f_g = f_greenwalds[i] if not np.isnan(f_greenwalds[i]) else f_g_default
        tau_pred = tau_bases[i] * C * (rho_stars[i]**alpha_rat) * (nu_stars[i]**beta_rat) * \
                   (epsilons[i]**gamma_rat) * (f_g**delta)
        preds.append(tau_pred)
        errors.append(abs(tau_pred - tau_exps[i]) / tau_exps[i])
    return np.mean(errors) * 100, np.array(preds), np.array(errors) * 100

# Find optimal delta
def objective(params):
    C, delta = params
    err, _, _ = compute_error_with_greenwald(C, delta)
    return err

result = minimize(objective, [C_gemini, 0.0], bounds=[(1, 20), (-2, 2)])
C_opt, delta_opt = result.x

print(f"\nOptimal parameters with Greenwald term:")
print(f"  C = {C_opt:.4f} (vs 3π/√2 = {C_gemini:.4f})")
print(f"  δ (Greenwald exponent) = {delta_opt:.4f}")

err_with_g, preds_with_g, errs_with_g = compute_error_with_greenwald(C_opt, delta_opt)

print(f"\nFormula: τ_E = {C_opt:.2f} × (a²κ/χ_gB) × ρ*^(-5/8) × ν*^(-2/7) × ε^(-5/4) × f_G^{delta_opt:.3f}")
print()
print(f"{'Machine':<10}{'τ_pred':>10}{'τ_exp':>10}{'Error%':>10}{'Δ Error':>10}")
print("-"*50)
for i in range(len(machines)):
    delta_err = errs_with_g[i] - errors_base[i]
    better = "✓" if delta_err < -5 else ""
    print(f"{names[i]:<10}{preds_with_g[i]:>10.4f}{tau_exps[i]:>10.4f}{errs_with_g[i]:>9.1f}%{delta_err:>+9.1f}% {better}")

print(f"\nMean error: {err_with_g:.1f}% (was {np.mean(errors_base):.1f}%)")
gap_new = np.max(preds_with_g/tau_exps) / np.min(preds_with_g/tau_exps)
print(f"Gap ratio: {gap_new:.4f}")

# ============================================================================
# STEP 5: Try normalized current I_p* = I_p/(a*B) instead
# ============================================================================
print("\n" + "-"*80)
print("STEP 5: TRY NORMALIZED CURRENT I_p* = I_p/(a×B)")
print("-"*80)

# This is the Alfvén current normalization
I_p_stars = []
for i, m in enumerate(machines):
    if I_ps[i] > 0:
        I_p_star = I_ps[i] / (a_values[i] * m["B_T"])
        I_p_stars.append(I_p_star)
    else:
        I_p_stars.append(np.nan)

I_p_stars = np.array(I_p_stars)

print(f"\n{'Machine':<10}{'I_p (MA)':>10}{'a×B':>10}{'I_p*':>10}")
print("-"*40)
for i in range(len(machines)):
    if not np.isnan(I_p_stars[i]):
        print(f"{names[i]:<10}{I_ps[i]:>10.1f}{a_values[i]*machines[i]['B_T']:>10.2f}{I_p_stars[i]:>10.3f}")
    else:
        print(f"{names[i]:<10}{'N/A':>10}{'N/A':>10}{'N/A':>10}")

# Fit with I_p*
def compute_error_with_Ipstar(C, delta, I_p_default=0.5):
    errors = []
    preds = []
    for i in range(len(machines)):
        I_p_s = I_p_stars[i] if not np.isnan(I_p_stars[i]) else I_p_default
        tau_pred = tau_bases[i] * C * (rho_stars[i]**alpha_rat) * (nu_stars[i]**beta_rat) * \
                   (epsilons[i]**gamma_rat) * (I_p_s**delta)
        preds.append(tau_pred)
        errors.append(abs(tau_pred - tau_exps[i]) / tau_exps[i])
    return np.mean(errors) * 100, np.array(preds), np.array(errors) * 100

def objective2(params):
    C, delta = params
    err, _, _ = compute_error_with_Ipstar(C, delta)
    return err

result2 = minimize(objective2, [C_gemini, 0.5], bounds=[(1, 20), (-2, 2)])
C_opt2, delta_opt2 = result2.x

err_with_Ip, preds_with_Ip, errs_with_Ip = compute_error_with_Ipstar(C_opt2, delta_opt2)

print(f"\nOptimal with I_p* term:")
print(f"  C = {C_opt2:.4f}")
print(f"  δ (current exponent) = {delta_opt2:.4f}")
print(f"  Mean error: {err_with_Ip:.1f}%")

# ============================================================================
# STEP 6: The safety factor q connection
# ============================================================================
print("\n" + "-"*80)
print("STEP 6: SAFETY FACTOR q = ε × B × a / (μ₀ × I_p × κ)")
print("-"*80)

# q_95 approximation: q ~ (5 * a² * B * κ) / (R * I_p)
# This connects ε, B, and I_p into one dimensionless number

q_values = []
for i, m in enumerate(machines):
    if I_ps[i] > 0:
        a = a_values[i]
        R = m["R"]
        B = m["B_T"]
        kappa = m["kappa"]
        I_p = I_ps[i] * 1e6  # Convert MA to A
        
        # q_95 ≈ 5 * a² * B * κ / (R * μ₀ * I_p / 2π)
        # Simplified: q ~ (2π × a² × B × κ) / (μ₀ × R × I_p)
        q_approx = (2 * np.pi * a**2 * B * kappa) / (mu_0 * R * I_p)
        q_values.append(q_approx)
    else:
        # Stellarators: use transformation iota ~ 1/ε
        q_values.append(1.0 / m["epsilon"])

q_values = np.array(q_values)

print(f"\n{'Machine':<10}{'q_approx':>10}{'ε':>10}{'q × ε':>10}")
print("-"*40)
for i in range(len(machines)):
    print(f"{names[i]:<10}{q_values[i]:>10.3f}{epsilons[i]:>10.3f}{q_values[i]*epsilons[i]:>10.3f}")

# Test: does q help?
def compute_error_with_q(C, delta, alpha=alpha_rat, beta_exp=beta_rat, gamma=gamma_rat):
    errors = []
    preds = []
    for i in range(len(machines)):
        tau_pred = tau_bases[i] * C * (rho_stars[i]**alpha) * (nu_stars[i]**beta_exp) * \
                   (epsilons[i]**gamma) * (q_values[i]**delta)
        preds.append(tau_pred)
        errors.append(abs(tau_pred - tau_exps[i]) / tau_exps[i])
    return np.mean(errors) * 100, np.array(preds), np.array(errors) * 100

def objective_q(params):
    C, delta = params
    err, _, _ = compute_error_with_q(C, delta)
    return err

result_q = minimize(objective_q, [C_gemini, 0.0], bounds=[(1, 20), (-2, 2)])
C_opt_q, delta_opt_q = result_q.x

err_with_q, preds_with_q, errs_with_q = compute_error_with_q(C_opt_q, delta_opt_q)

print(f"\nOptimal with q term:")
print(f"  C = {C_opt_q:.4f}")
print(f"  δ (q exponent) = {delta_opt_q:.4f}")

print(f"\nFormula: τ_E = {C_opt_q:.2f} × (a²κ/χ_gB) × ρ*^(-5/8) × ν*^(-2/7) × ε^(-5/4) × q^{delta_opt_q:.3f}")
print()
print(f"{'Machine':<10}{'τ_pred':>10}{'τ_exp':>10}{'Error%':>10}{'Δ Error':>10}")
print("-"*50)
for i in range(len(machines)):
    delta_err = errs_with_q[i] - errors_base[i]
    better = "✓" if delta_err < -5 else ""
    print(f"{names[i]:<10}{preds_with_q[i]:>10.4f}{tau_exps[i]:>10.4f}{errs_with_q[i]:>9.1f}%{delta_err:>+9.1f}% {better}")

print(f"\nMean error: {err_with_q:.1f}% (was {np.mean(errors_base):.1f}%)")
gap_q = np.max(preds_with_q/tau_exps) / np.min(preds_with_q/tau_exps)
print(f"Gap ratio: {gap_q:.4f}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("FINAL COMPARISON")
print("="*80)

print(f"""
{'Formula':<35}{'Mean Error':>12}{'Gap Ratio':>12}{'JET err':>10}{'JT-60U err':>12}

Base (no current)                   {np.mean(errors_base):>10.1f}%  {np.max(preds_with_q/tau_exps)/np.min(preds_with_q/tau_exps):>10.4f}    {errors_base[0]:>8.1f}%    {errors_base[3]:>10.1f}%
+ Greenwald f_G^{delta_opt:.2f}               {err_with_g:>10.1f}%  {gap_new:>10.4f}    {errs_with_g[0]:>8.1f}%    {errs_with_g[3]:>10.1f}%
+ Safety factor q^{delta_opt_q:.2f}            {err_with_q:>10.1f}%  {gap_q:>10.4f}    {errs_with_q[0]:>8.1f}%    {errs_with_q[3]:>10.1f}%
""")

# What is the rational fraction closest to delta_opt_q?
print("\n" + "-"*80)
print("THEORETICAL INTERPRETATION")
print("-"*80)

fractions = [(n, d, n/d) for d in range(1, 8) for n in range(-7, 8) if d > 0]
closest = min(fractions, key=lambda x: abs(x[2] - delta_opt_q))
print(f"\nFitted q exponent: {delta_opt_q:.4f}")
print(f"Closest rational fraction: {closest[0]}/{closest[1]} = {closest[2]:.4f}")

# The IPB98 has I_p^0.93 ≈ I_p^(14/15)
# In our formula, q ~ 1/I_p, so q^δ ~ I_p^(-δ)
# If δ ≈ -0.93, then we'd recover IPB98's current dependence
print(f"\nIPB98 has I_p^0.93 ≈ I_p^(14/15)")
print(f"Since q ~ 1/I_p, a q^{delta_opt_q:.2f} term is equivalent to I_p^{-delta_opt_q:.2f}")
print(f"This {'matches' if abs(-delta_opt_q - 0.93) < 0.3 else 'differs from'} the IPB98 current scaling.")
