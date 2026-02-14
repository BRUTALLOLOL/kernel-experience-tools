"""
Kernel-Experience Tools: A library for projecting memory kernels to experience functions.
"""

# Use try-except for compatibility
try:
    # Absolute imports (preferred)
    from kernel_experience.kernel import Kernel
    from kernel_experience.projection import project_kernel_to_n, project_to_envelope_n, compute_accuracy
    from kernel_experience.solvers import solve_volterra
except ImportError:
    # Relative imports as fallback
    from .kernel import Kernel
    from .projection import project_kernel_to_n, project_to_envelope_n, compute_accuracy
    from .solvers import solve_volterra

__version__ = "1.0.1"
__author__ = "Artem Vozmishchev"
__email__ = "xbrutallololx@gmail.com"

__all__ = [
    "Kernel",
    "project_kernel_to_n",
    "project_to_envelope_n",
    "compute_accuracy",
    "solve_volterra"
]

