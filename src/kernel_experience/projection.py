"""
Projection algorithms: K(t) → n(t).
"""

import numpy as np
from typing import Tuple, Union
from .kernel import Kernel
from .solvers import solve_volterra


def project_kernel_to_n(kernel: Kernel,
                        lambda_param: float = 0.8,
                        t_max: float = 10.0,
                        n_points: int = 1000,
                        x0: float = 1.0,
                        return_complex: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Main projection: K(t) → n(t).

    Parameters
    ----------
    kernel : Kernel
        Memory kernel.
    lambda_param : float
        Parameter λ in (0, 1).
    t_max : float
        Maximum time.
    n_points : int
        Number of time points.
    x0 : float
        Initial condition.
    return_complex : bool
        If True, return complex n(t) for oscillatory kernels.

    Returns
    -------
    t : np.ndarray
        Time grid.
    x : np.ndarray
        Solution x(t).
    n : np.ndarray
        Experience function n(t) (real or complex).
    """
    # 1. Solve Volterra equation
    t, x = solve_volterra(kernel, t_max, n_points, x0)

    # 2. Compute n(t) = log_λ(x(t)/x0)
    ratio = x / x0

    if return_complex:
        # Complex logarithm for oscillatory solutions
        n_real = np.log(np.abs(ratio)) / np.log(lambda_param)
        n_imag = np.angle(ratio) / np.log(lambda_param)
        n = n_real + 1j * n_imag
    else:
        # Real logarithm (enforce positivity)
        ratio = np.maximum(ratio, 1e-12)  # Avoid log(0)
        n = np.log(ratio) / np.log(lambda_param)

    return t, x, n


def project_to_envelope_n(kernel: Kernel,
                          lambda_param: float = 0.8,
                          t_max: float = 10.0,
                          n_points: int = 1000,
                          x0: float = 1.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Project to monotonic envelope of n(t).

    Uses Hilbert transform to extract envelope of oscillatory solutions.
    """
    from scipy.signal import hilbert

    t, x, n_complex = project_kernel_to_n(
        kernel, lambda_param, t_max, n_points, x0, return_complex=True
    )

    # Extract envelope via Hilbert transform
    analytic_signal = hilbert(x.real)
    envelope = np.abs(analytic_signal)

    # Compute envelope n(t)
    ratio_env = envelope / x0
    ratio_env = np.maximum(ratio_env, 1e-12)
    n_env = np.log(ratio_env) / np.log(lambda_param)

    # Ensure monotonic decrease (accumulated minimum)
    n_env_mono = np.minimum.accumulate(n_env)

    return t, envelope, n_env_mono


def compute_accuracy(original_x: np.ndarray,
                     reconstructed_x: np.ndarray) -> dict:
    """
    Compute accuracy metrics between original and reconstructed solutions.
    """
    mask = original_x != 0
    rel_error = np.abs(original_x[mask] - reconstructed_x[mask]) / np.abs(original_x[mask])

    return {
        'mean_error': float(np.mean(rel_error)),
        'max_error': float(np.max(rel_error)),
        'accuracy': float(1 - np.mean(rel_error)),
        'rmse': float(np.sqrt(np.mean((original_x - reconstructed_x) ** 2)))
    }