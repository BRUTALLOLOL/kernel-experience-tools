```markdown
# Kernel-Experience Tools

**A Python library for projecting memory kernels to experience functions.**

---

## 📌 What is it?

This library implements a numerical method that takes a memory kernel `K(t)` from a Volterra relaxation equation

```
x(t) = x₀ - ∫₀ᵗ K(t-τ) x(τ) dτ
```

and finds a unique experience function `n(t)` such that

```
x(t) = x₀ · λⁿ⁽ᵗ⁾
```

The function `n(t)` encodes the entire memory history in a single curve.

---

## 📦 Installation

```bash
pip install git+https://github.com/BRUTALLOLOL/kernel-experience-tools
```

---

## 🚀 Quick start

```python
from kernel_experience import Kernel, project_kernel_to_n

# Define a kernel
K = Kernel.tempered_power_law(alpha=0.6, beta=0.3)

# Project to experience function
t, x, n = project_kernel_to_n(K, t_max=10)

print(f"Memory score: {n[-1]:.2f}")
# Memory score: 3.44
```

---

## 📘 API Reference

### `Kernel`

Container for memory kernel with metadata.

**Parameters:**
- `func`: callable — Kernel function K(t)
- `name`: str, optional — Kernel name (default: "CustomKernel")
- `params`: dict, optional — Kernel parameters

**Factory methods:**

```python
# Exponential kernel: K(t) = γ·e^{-γt}
K = Kernel.exponential(gamma=1.0)

# Power law kernel: K(t) = γ·t^{α-1}/Γ(α)
K = Kernel.power_law(alpha=0.7, gamma=1.0)

# Mittag-Leffler kernel: K(t) = t^{α-1}E_{α,α}(-t^α)
K = Kernel.mittag_leffler(alpha=0.7, beta=1.0)

# Tempered power law: K(t) = γ·t^{α-1}e^{-βt}/Γ(α)
K = Kernel.tempered_power_law(alpha=0.6, beta=0.3, gamma=1.0)
```

**Custom kernel:**

```python
def my_kernel(t):
    return np.exp(-t) * np.cos(t)

K = Kernel(my_kernel, name="Oscillatory", params={"freq": 1.0})
```

---

### `project_kernel_to_n()`

Main projection: K(t) → n(t).

**Parameters:**
- `kernel`: Kernel — Memory kernel
- `lambda_param`: float, default=0.8 — Base λ in (0,1)
- `t_max`: float, default=10.0 — Maximum time
- `n_points`: int, default=1000 — Number of time points
- `x0`: float, default=1.0 — Initial condition
- `return_complex`: bool, default=False — Return complex n(t) for oscillatory kernels

**Returns:**
- `t`: ndarray — Time grid
- `x`: ndarray — Solution x(t)
- `n`: ndarray — Experience function n(t)

**Examples:**

```python
# Basic usage
t, x, n = project_kernel_to_n(K, t_max=20, n_points=2000)

# Custom lambda (faster/slower experience accumulation)
t, x, n = project_kernel_to_n(K, lambda_param=0.5)

# Oscillatory kernel — get complex n(t)
K_osc = Kernel(lambda t: np.exp(-0.1*t)*np.sin(t), name="Oscillatory")
t, x, n_complex = project_kernel_to_n(K_osc, return_complex=True)

# Extract real and imaginary parts
n_real = n_complex.real
n_imag = n_complex.imag
```

---

### `solve_volterra()`

Numerical solver for Volterra integral equation.

**Parameters:**
- `kernel`: Kernel — Memory kernel
- `t_max`: float, default=10.0 — Maximum time
- `n_points`: int, default=1000 — Number of time points
- `x0`: float, default=1.0 — Initial condition

**Returns:**
- `t`: ndarray — Time grid
- `x`: ndarray — Solution x(t)

**Example:**

```python
t, x = solve_volterra(K, t_max=5, n_points=500)
```

---

### `compute_accuracy()`

Compare original and reconstructed solutions.

**Parameters:**
- `original_x`: ndarray — Original solution x(t)
- `reconstructed_x`: ndarray — Reconstructed solution x₀·λⁿ⁽ᵗ⁾

**Returns:**
- `dict`: Accuracy metrics

**Example:**

```python
# Get solution and n(t)
t, x, n = project_kernel_to_n(K)

# Reconstruct from n(t)
x_rec = 1.0 * (0.8 ** n)

# Check accuracy
metrics = compute_accuracy(x, x_rec)
print(f"Accuracy: {metrics['accuracy']:.2%}")
print(f"Mean error: {metrics['mean_error']:.2e}")
# Output: Accuracy: 100.00%
# Output: Mean error: 1.23e-12
```

---

## 🧠 What problem does it solve?

Traditional relaxation models assume exponential decay.  
Real systems (glasses, polymers, biological tissues) show memory effects — power laws, stretched exponentials, oscillations.

This library provides one unified representation for all memory kernels:

```
K(t) → n(t)
```

Once you have `n(t)`, the relaxation curve is simply `x₀ · λⁿ⁽ᵗ⁾`.

---

## 📄 Citation

```bibtex
@software{vozmishchev2026kernel,
  author = {Vozmishchev, Artem},
  title = {Kernel-Experience Tools: Projecting Memory Kernels to Experience Functions},
  year = {2026},
  doi = {10.5281/zenodo.18239294},
  url = {https://zenodo.org/records/18239294}
}
```

---

## 📜 License

MIT License
