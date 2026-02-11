"""
Kernel class for memory kernels K(t).
"""

import numpy as np
from typing import Callable, Union, List
from dataclasses import dataclass


@dataclass
class Kernel:
    """
    Memory kernel representation.

    Parameters
    ----------
    func : callable
        Function K(t) that returns kernel value at time t.
    name : str, optional
        Human-readable name of the kernel.
    params : dict, optional
        Dictionary of kernel parameters.
    """
    func: Callable[[float], float]
    name: str = "CustomKernel"
    params: dict = None

    def __post_init__(self):
        if self.params is None:
            self.params = {}

    def __call__(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Evaluate kernel at time t."""
        return self.func(t)

    def __repr__(self):
        return f"Kernel(name='{self.name}', params={self.params})"

    # Factory methods for common kernels
    @classmethod
    def exponential(cls, gamma: float = 1.0):
        """Exponential kernel: K(t) = γ * e^{-γt}"""

        def func(t):
            return gamma * np.exp(-gamma * np.maximum(t, 0))

        return cls(func=func, name="Exponential", params={"gamma": gamma})

    @classmethod
    def power_law(cls, alpha: float = 0.5, gamma: float = 1.0):
        """Power-law kernel: K(t) = γ * t^(α-1) / Γ(α)"""
        from scipy.special import gamma as gamma_func
        prefactor = gamma / gamma_func(alpha)

        def func(t):
            t_safe = np.where(t > 0, t, 1e-12)  # Избегаем деления на ноль
            return prefactor * np.power(t_safe, alpha - 1)

        return cls(func=func, name="PowerLaw",
                   params={"alpha": alpha, "gamma": gamma})

    @classmethod
    def mittag_leffler(cls, alpha: float = 0.7, beta: float = 1.0):
        """Mittag-Leffler kernel: K(t) = t^(α-1) * E_{α,α}(-t^α)"""
        from scipy.special import gamma

        def func(t):
            # Simplified version - in practice use ml() from scipy
            t_alpha = np.power(t, alpha)
            return np.power(t, alpha - 1) * np.exp(-t_alpha) / gamma(alpha)

        return cls(func=func, name="MittagLeffler",
                   params={"alpha": alpha, "beta": beta})

    @classmethod
    def tempered_power_law(cls, alpha: float = 0.6, beta: float = 0.3, gamma: float = 1.0):
        """Tempered power-law: K(t) = γ * t^(α-1) * e^{-βt} / Γ(α)"""
        from scipy.special import gamma as gamma_func
        prefactor = gamma / gamma_func(alpha)

        def func(t):
            t_safe = np.where(t > 0, t, 1e-12)
            return prefactor * np.power(t_safe, alpha - 1) * np.exp(-beta * t_safe)

        return cls(func=func, name="TemperedPowerLaw",
                   params={"alpha": alpha, "beta": beta, "gamma": gamma})