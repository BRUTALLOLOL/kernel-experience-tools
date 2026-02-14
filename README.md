# Kernel-Experience Tools 🧠 → ⏳

**A Python library that turns memory kernels into experience functions.**

---

## 📌 What is it?

Every memory kernel K(t) hides a story.

This library finds it.

Given the Volterra relaxation equation

x(t) = x₀ - ∫₀ᵗ K(t-τ) x(τ) dτ

we compute the unique experience function n(t) such that

x(t) = x₀ · λⁿ⁽ᵗ⁾

One kernel. One curve. One number.

---

## 🚀 Quick start

```python
from kernel_experience import Kernel, project_kernel_to_n

# Pick a kernel
K = Kernel.tempered_power_law(alpha=0.6, beta=0.3)

# Get its experience function
t, x, n = project_kernel_to_n(K, t_max=10)

print(f"Memory score: {n[-1]:.2f}")
# Memory score: 3.44
```

---

## 📦 Installation

```bash
pip install kernel-experience-tools
```

---

## 📘 API Reference

### Kernel

Container for your memory kernel.

**Parameters**

- `func`: callable — Kernel function K(t)
- `name`: str, optional — Kernel name (default: "CustomKernel")
- `params`: dict, optional — Kernel parameters

**Factory methods**

```python
# Exponential: γ·e^{-γt}
K = Kernel.exponential(gamma=1.0)

# Power law: γ·t^{α-1}/Γ(α)
K = Kernel.power_law(alpha=0.7, gamma=1.0)

# Mittag-Leffler: t^{α-1}E_{α,α}(-t^α)
K = Kernel.mittag_leffler(alpha=0.7)

# Tempered power law: γ·t^{α-1}e^{-βt}/Γ(α)
K = Kernel.tempered_power_law(alpha=0.6, beta=0.3, gamma=1.0)
```

**Custom kernel**

```python
def my_kernel(t):
    return np.exp(-t) * np.cos(t)

K = Kernel(my_kernel, name="Oscillatory", params={"freq": 1.0})
```

---

### project_kernel_to_n

Main projection: K(t) → n(t).

**Parameters**

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `kernel` | `Kernel` | — | Memory kernel |
| `lambda_param` | `float` | 0.8 | Base λ in (0,1) |
| `t_max` | `float` | 10.0 | Maximum time |
| `n_points` | `int` | 1000 | Number of time points |
| `x0` | `float` | 1.0 | Initial condition |
| `return_complex` | `bool` | False | Return complex n(t) for oscillatory kernels |

**Returns**

| Return | Type | Description |
|--------|------|-------------|
| `t` | `ndarray` | Time grid |
| `x` | `ndarray` | Solution x(t) |
| `n` | `ndarray` | Experience function n(t) |

**Examples**

```python
# Basic usage
t, x, n = project_kernel_to_n(K, t_max=20, n_points=2000)

# Custom lambda
t, x, n = project_kernel_to_n(K, lambda_param=0.5)

# Oscillatory kernel — get complex n(t)
K_osc = Kernel(lambda t: np.exp(-0.1*t)*np.sin(t), name="Oscillatory")
t, x, n_complex = project_kernel_to_n(K_osc, return_complex=True)

# Extract real and imaginary parts
n_real = n_complex.real
n_imag = n_complex.imag
```

---

### solve_volterra

Numerical solver for Volterra integral equation.

**Parameters**

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `kernel` | `Kernel` | — | Memory kernel |
| `t_max` | `float` | 10.0 | Maximum time |
| `n_points` | `int` | 1000 | Number of time points |
| `x0` | `float` | 1.0 | Initial condition |

**Returns**

| Return | Type | Description |
|--------|------|-------------|
| `t` | `ndarray` | Time grid |
| `x` | `ndarray` | Solution x(t) |

**Example**

```python
t, x = solve_volterra(K, t_max=5, n_points=500)
```

---

### compute_accuracy

Compare original and reconstructed solutions.

**Parameters**

| Parameter | Type | Description |
|----------|------|-------------|
| `original_x` | `ndarray` | Original solution x(t) |
| `reconstructed_x` | `ndarray` | Reconstructed solution x₀·λⁿ⁽ᵗ⁾ |

**Returns**

| Return | Type | Description |
|--------|------|-------------|
| `dict` | `dict` | Accuracy metrics |

**Metrics**

- `mean_error`: float — Mean relative error
- `max_error`: float — Maximum relative error
- `accuracy`: float — 1 - mean_error
- `rmse`: float — Root mean square error

**Example**

```python
# Get solution and n(t)
t, x, n = project_kernel_to_n(K)

# Reconstruct from n(t)
x_rec = 1.0 * (0.8 ** n)

# Check accuracy
metrics = compute_accuracy(x, x_rec)
print(f"Accuracy: {metrics['accuracy']:.2%}")
print(f"Mean error: {metrics['mean_error']:.2e}")
# Accuracy: 100.00%
# Mean error: 1.23e-12
```

---

## 🧠 What problem does it solve?

Traditional relaxation models assume exponential decay.

Real systems — glasses, polymers, biological tissues — show memory effects. Power laws. Stretched exponentials. Oscillations.

This library gives you one language for all of them:

K(t) → n(t)

Once you have n(t), the relaxation curve is simply x₀ · λⁿ⁽ᵗ⁾.

No fractional calculus. No special functions. No black boxes.

Just your kernel. One function call. One curve.

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

---

**Now go find what your kernel remembers.**

