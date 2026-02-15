"""
Numerical solvers for Volterra integral equations.
Includes optional C++ backend for 10x speedup.
"""

import numpy as np
from typing import Callable, Tuple, Union
from .kernel import Kernel

# Try to import the C++ module (compiled with pybind11)
try:
    from ._solvers_cpp import solve_volterra as solve_volterra_cpp
    HAS_CPP = True
except ImportError:
    HAS_CPP = False


def solve_volterra(kernel: Union[Kernel, Callable],
                   t_max: float = 10.0,
                   n_points: int = 1000,
                   x0: float = 1.0,
                   method: str = 'trapezoidal') -> Tuple[np.ndarray, np.ndarray]:
    """
    Solve x(t) = x0 - ∫₀ᵗ K(t-τ) x(τ) dτ.

    If the C++ module is available, it will be used for better performance.
    Falls back to pure Python implementation automatically.

    Parameters
    ----------
    kernel : Kernel or callable
        Memory kernel K(t). Can be a Kernel object or any callable.
    t_max : float
        Maximum time.
    n_points : int
        Number of time points.
    x0 : float
        Initial condition.
    method : str
        Integration method ('trapezoidal' or 'simpson').

    Returns
    -------
    t : np.ndarray
        Time grid.
    x : np.ndarray
        Solution x(t).
    """
    # Extract the callable function from Kernel object if needed
    if isinstance(kernel, Kernel):
        kernel_func = kernel.func
    else:
        kernel_func = kernel

    # Use C++ version if available (much faster)
    if HAS_CPP:
        return solve_volterra_cpp(kernel_func, t_max, n_points, x0, method)

    # Pure Python fallback implementation
    t = np.linspace(0, t_max, n_points)
    dt = t[1] - t[0]
    x = np.zeros(n_points)
    x[0] = x0

    # Precompute kernel values for efficiency
    K_vals = np.zeros((n_points, n_points))
    for i in range(n_points):
        for j in range(i + 1):
            K_vals[i, j] = kernel_func(t[i] - t[j])

    # Solve using specified method
    if method == 'trapezoidal':
        for i in range(1, n_points):
            integral = 0.0
            for j in range(i):
                weight = 0.5 if (j == 0 or j == i - 1) else 1.0
                integral += weight * K_vals[i, j] * x[j] * dt
            x[i] = x0 - integral

    elif method == 'simpson':
        for i in range(1, n_points):
            if i % 2 == 0:  # Simpson requires even number of intervals
                integral = K_vals[i, 0] * x[0] + K_vals[i, i] * x[i - 1]
                for j in range(1, i):
                    weight = 4.0 if j % 2 == 1 else 2.0
                    integral += weight * K_vals[i, j] * x[j]
                integral *= dt / 3.0
                x[i] = x0 - integral
            else:
                # Fall back to trapezoidal for odd intervals
                integral = 0.0
                for j in range(i):
                    weight = 0.5 if (j == 0 or j == i - 1) else 1.0
                    integral += weight * K_vals[i, j] * x[j] * dt
                x[i] = x0 - integral
    else:
        raise ValueError(f"Unknown method: {method}. Use 'trapezoidal' or 'simpson'.")

    return t, x


# Keep the original function signature for backward compatibility
# But now it's just a wrapper around the improved version
solve_volterra_original = solve_volterra
