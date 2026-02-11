"""
Kernel-Experience Tools: A library for projecting memory kernels to experience functions.
"""

from .kernel import Kernel
from .projection import project_kernel_to_n, project_to_envelope_n, compute_accuracy
from .solvers import solve_volterra

__version__ = "0.1.0"
__author__ = "Artem Vozmishchev"
__email__ = "your.email@example.com"

__all__ = [
    "Kernel",
    "project_kernel_to_n",
    "project_to_envelope_n",
    "compute_accuracy",
    "solve_volterra"
]