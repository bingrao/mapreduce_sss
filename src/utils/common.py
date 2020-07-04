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


def lagrange_interpolate(xs, ys):
    return CustomPolynomial(lagrange(xs, ys)).coef[-1]
