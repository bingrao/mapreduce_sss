from functools import reduce
from src.utils.polynomial import CustomPolynomial
import numpy as np
from numpy.random import default_rng
from scipy.interpolate import lagrange
from decimal import *
from itertools import islice
from sage.all import ZZ


# find a number in a list
# not find, return -1
def find_in_list(tem, lxs):
    lenlist = len(lxs)
    ret = -1
    for x in range(lenlist):
        if lxs[x] == tem:
            ret = x
            break
    return ret


# generate n randome numbers, not repeated
def generate_random_with_sage(n, zp):
    l_xs = []
    tem = zp.random_element()
    while tem == 0:
        tem = zp.random_element()
    l_xs.append(tem)
    while len(l_xs) < n:
        tem = zp.random_element()
        while tem == 0:
            tem = zp.random_element()
        if find_in_list(tem, l_xs) < 0:
            l_xs.append(tem)
    return l_xs

# https://ask.sagemath.org/question/43657/list-of-random-non-zero-elements/
# def generate_random_with_sage(nums, zp):
#     return list(islice(filter(lambda x: x != 0, (zp.random_element() for _ in ZZ)), nums))


def generate_random(min=1, max=100, nums=10):
    rng = default_rng()
    numbers = rng.choice(np.arange(min, max), size=nums, replace=False)
    return numbers


def generate_random_coefficients(secret, poly_order, zp=None):
    reg = np.append(secret, generate_random(min=1, max=10, nums=poly_order)) if zp is None \
        else np.append(secret, generate_random_with_sage(poly_order, zp))
    return reg


# We provide three different kinds of lagrange interpolate method to recover data
# shares: [(x1, y1), (x2, y2), ..., (xn, yn)]
#
def lagrange_interpolate(shares):
    xs = [idx for idx, _ in shares]
    ys = [share for _, share in shares]
    return CustomPolynomial(lagrange(xs, ys)).coef[-1]


def interpolate(shares, x=0):
    x_values = [idx for idx, _ in shares]
    y_values = [share for _, share in shares]

    def _basis(j):
        p = [(x - x_values[m]) / (x_values[j] - x_values[m]) for m in range(k) if m != j]
        return reduce(np.multiply, p)

    assert len(x_values) != 0 and (len(x_values) == len(y_values)), \
        "x and y cannot be empty and must have the same length"
    k = len(x_values)
    return sum(_basis(j) * y_values[j] for j in range(k))


# https://www.geeksforgeeks.org/implementing-shamirs-secret-sharing-scheme-in-python/
def interpolate_decimal(shares):
    # Combines shares using
    # Lagranges interpolation.
    # Shares is an array of shares
    # being combined
    sums, prod_arr = 0, []

    for j in range(len(shares)):
        xj, yj = shares[j][0], shares[j][1]
        prod = Decimal(1)

        for i in range(len(shares)):
            xi = shares[i][0]
            if i != j:
                prod *= Decimal(Decimal(xi) / (xi - xj))

        prod *= yj
        sums += Decimal(prod)

    return int(round(Decimal(sums), 0))
