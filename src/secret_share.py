# import sage.all
# from sage.arith.misc import random_prime
# from sage.rings.finite_rings.all import GF
from polynomial import Polynomial
from utils.context import Context
import numpy as np
from numpy.random import default_rng

class SecretShare:
    def __init__(self, ctx):
        self.context = ctx
        # self.nums_prime = random_prime(2 ** 10)
        # self.zp = GF(self.nums_prime)

    @staticmethod
    def generate_random_coefficients(self, secret, poly_order=1):
        rng = default_rng()
        numbers = rng.choice(100, size=poly_order, replace=False)
        return np.append(numbers, secret)
        # return [self.zp.random_element() for _ in range(poly_order)] + [secret]

    def create_shares(self, secret, poly_order=1, nums_shares=10, idents_shares=None):
        x_values = idents_shares if idents_shares is not None else list(range(1, nums_shares + 1))
        coefficients = self.generate_random_coefficients(secret, poly_order)
        polynomial_funcs = Polynomial(coefficients)
        logging.debug(f"Polynomial Functions {str(polynomial_funcs)}")
        logging.debug(f"The x values: {x_values}")
        return [polynomial_funcs(x) for x in x_values]


if __name__ == "__main__":
    context = Context(desc="Secret Share")
    logging = context.logger
    share_engine = SecretShare(context)
    secret = 10
    secret_shares = share_engine.create_shares(secret, poly_order=2)
    logging.info(f"The Secret is {secret} --> {secret_shares}")

