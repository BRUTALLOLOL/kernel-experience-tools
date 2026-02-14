"""
Kernel-Experience Tools: A library for projecting memory kernels to experience functions.
"""

# Use try-except for compatibility
try:
    # Absolute imports (preferred)
    from kernel_experience.kernel import Kernel
    from kernel_experience.projection import project_kernel_to_n, project_to_envelope_n, compute_accuracy
    from kernel_experience.solvers import solve_volterra
    from kernel_experience.convert import lambda_to_exp, exp_to_lambda, lambda_scale_factor
except ImportError:
    # Relative imports as fallback
    from .kernel import Kernel
    from .projection import project_kernel_to_n, project_to_envelope_n, compute_accuracy
    from .solvers import solve_volterra
    from .convert import lambda_to_exp, exp_to_lambda, lambda_scale_factor

__version__ = "0.2.0"
__author__ = "Artem Vozmishchev"
__email__ = "xbrutallololx@gmail.com"

__all__ = [
    "Kernel",
    "project_kernel_to_n",
    "project_to_envelope_n",
    "compute_accuracy",
    "solve_volterra",
    "lambda_to_exp",        
    "exp_to_lambda",
    "lambda_scale_factor",
]
