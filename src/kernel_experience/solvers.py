"""
Numerical solvers for Volterra integral equations.
"""

import numpy as np
from typing import Callable, Tuple
from .kernel import Kernel


def solve_volterra(kernel: Kernel,
                   t_max: float = 10.0,
                   n_points: int = 1000,
                   x0: float = 1.0,
                   method: str = 'trapezoidal') -> Tuple[np.ndarray, np.ndarray]:
    """
    Solve x(t) = x0 - ∫₀ᵗ K(t-τ) x(τ) dτ.

    Parameters
    ----------
    kernel : Kernel
        Memory kernel K(t).
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
    t = np.linspace(0, t_max, n_points)
    dt = t[1] - t[0]
    x = np.zeros(n_points)
    x[0] = x0

    # Precompute kernel values for efficiency
    K_vals = np.zeros((n_points, n_points))
    for i in range(n_points):
        for j in range(i + 1):
            K_vals[i, j] = kernel(t[i] - t[j])

    # Solve using specified method
    if method == 'trapezoidal':
        for i in range(1, n_points):
            integral = 0
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
                integral = 0
                for j in range(i):
                    weight = 0.5 if (j == 0 or j == i - 1) else 1.0
                    integral += weight * K_vals[i, j] * x[j] * dt
                x[i] = x0 - integral

    return t, x