"""
Conversion between different lambda scales and experience units.
"""

import numpy as np

def lambda_to_exp(n: float, lambda_: float) -> float:
    """
    Convert experience n measured with given lambda to e-foldings (λ=1/e).

    Parameters
    ----------
    n : float
        Experience value in the original lambda scale.
    lambda_ : float
        Base lambda used (must be in (0,1)).

    Returns
    -------
    float
        Experience in exp units (e-foldings).

    Example
    -------
    >>> lambda_to_exp(3.05, 0.8)
    0.68   # примерно
    """
    if lambda_ <= 0 or lambda_ >= 1:
        raise ValueError("lambda_ must be in (0,1)")
    return -n * np.log(lambda_)


def exp_to_lambda(n_exp: float, target_lambda: float) -> float:
    """
    Convert experience from exp units back to a given lambda scale.

    Parameters
    ----------
    n_exp : float
        Experience in exp units (e-foldings).
    target_lambda : float
        Target lambda scale (must be in (0,1)).

    Returns
    -------
    float
        Experience in the target lambda scale.
    """
    if target_lambda <= 0 or target_lambda >= 1:
        raise ValueError("target_lambda must be in (0,1)")
    return n_exp / (-np.log(target_lambda))


def lambda_scale_factor(lambda_from: float, lambda_to: float) -> float:
    """
    Get multiplicative factor to convert experience from one lambda to another.

    n_to = n_from * factor

    Parameters
    ----------
    lambda_from : float
        Original lambda scale.
    lambda_to : float
        Target lambda scale.

    Returns
    -------
    float
        Conversion factor.
    """
    return np.log(lambda_from) / np.log(lambda_to)
