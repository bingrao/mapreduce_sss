from functools import reduce

from src.utils.polynomial import CustomPolynomial
import numpy as np
from numpy.random import default_rng
from scipy.interpolate import lagrange


def generate_random(min=1, max=100, nums=10):
    rng = default_rng()
    numbers = rng.choice(np.arange(min, max), size=nums, replace=False)
    return numbers


def generate_random_coefficients(secret, poly_order):
    reg = np.append(secret, generate_random(min=1, max=10, nums=poly_order))
    return reg


def lagrange_interpolate(recover_shares):
    """
    recover_shares: [(x1, y1), (x2, y2), ..., (xn, yn)]
    """
    xs = [idx for idx, _ in recover_shares]
    ys = [share for _, share in recover_shares]
    return CustomPolynomial(lagrange(xs, ys)).coef[-1]


def interpolate(recover_shares, x=0):
    x_values = [idx for idx, _ in recover_shares]
    y_values = [share for _, share in recover_shares]

    def _basis(j):
        p = [(x - x_values[m]) / (x_values[j] - x_values[m]) for m in range(k) if m != j]
        return reduce(np.multiply, p)

    assert len(x_values) != 0 and (len(x_values) == len(y_values)), \
        "x and y cannot be empty and must have the same length"
    k = len(x_values)
    return sum(_basis(j) * y_values[j] for j in range(k))
