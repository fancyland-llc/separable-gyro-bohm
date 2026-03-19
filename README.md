# Separable Gyro-Bohm Scaling for Fusion Energy Confinement

**BVP-7: Resolving the Isotope Sign Conflict**

Antonio P. Matos  
Fancyland LLC — Lattice OS research infrastructure  
March 2026

## Abstract

A separable gyro-Bohm scaling formula that resolves the sign conflict in isotope scaling predictions. The decomposition ρ* = √M × ρ*\_thermal separates size scaling from mass scaling, allowing independent exponents that match both the negative size correction and the positive isotope effect.

**Mean error: 15.2%** across 5 machines with measured confinement data (DIII-D, ASDEX-U, JT-60U, W7-X, LHD).

## The Formula

```
τ_E = C × (a²κ/χ_gB) × ρ*_thermal^(-5/8) × M^(+1/5) × ν*^(-2/7) × ε^(-5/4)
```

Where:

- **C = 3.5779** (fitted prefactor, 0.93% from √4π)
- **a** = minor radius (m)
- **κ** = elongation
- **χ_gB** = T/(eB) gyro-Bohm diffusivity (m²/s)
- **ρ\*\_thermal** = √(m_p T)/(eBa) thermal gyroradius
- **M** = ion mass number
- **ν\*** = collisionality
- **ε** = a/R inverse aspect ratio

## Key Result

| Exponent             | Value | Origin                              |
| -------------------- | ----- | ----------------------------------- |
| ρ\*\_thermal         | -5/8  | Empirical (Bohm-to-gyro-Bohm range) |
| M (isotope)          | +1/5  | Derived: zonal flow suppression     |
| ν\* (collisionality) | -2/7  | Derived: banana regime              |
| ε (aspect ratio)     | -5/4  | Derived: trapped particle fraction  |

The **positive isotope exponent** M^(+1/5) matches the empirical IPB98 result M^(+0.19) while resolving the theoretical sign conflict in standard gyro-Bohm formulations.

## Files

### Whitepaper

- `SEPARABLE_GYRO_BOHM_SCALING.pdf` — Compiled paper
- `SEPARABLE_GYRO_BOHM_SCALING.tex` — LaTeX source
- `SEPARABLE_GYRO_BOHM_SCALING.md` — Markdown version

### Code (`bvp_7_fusion_confinement/`)

- `bvp7_final_closure.py` — Zero-parameter model validation + stellarator holdout test
- `greenwald_diagnostic.py` — Current term elimination test
- `isotope_diagnostic.py` — Separable vs. conflated ρ\* comparison
- `jet_deep_dive.py` — JET D-T regime identification
- `*.json` — Final results from the Antigen Factory swarm runs

## Citation

```bibtex
@article{matos2026separable,
  title={Separable Gyro-Bohm Scaling for Fusion Energy Confinement: Resolving the Isotope Sign Conflict},
  author={Matos, Antonio P.},
  year={2026},
  doi={10.5281/zenodo.19117880},
  url={https://zenodo.org/records/19117880}
}
```

## License

CC BY 4.0

---

_Fancyland LLC — Lattice OS research infrastructure_  
_BVP-7 Closed: March 19, 2026_  
_The rabbit has been caught._
