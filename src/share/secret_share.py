from share.polynomial import CustomPolynomial
from src.utils.context import Context
from sage.all import *


class SecretShare:
    def __init__(self, ctx):
        self.context = ctx
        self.logging = ctx.logger
        self.zp = ctx.zp

    def feldman_vss(self, coefficients):
        return [(self.context.g ** coef) % self.context.p for coef in coefficients]

    def pedersen_vss(self, coefficients):
        return [(self.context.g ** coef) % self.context.p for coef in coefficients]

    def create_shares(self, secret, poly_order=1, nums_shares=10, idents_shares=None):

        # Cloud identifiers used to generate corresponding secret shares
        x_values = idents_shares if idents_shares is not None else list(range(1, nums_shares + 1))

        # A list of Coefficents of Polynomial functions: [secret, a1, a2, ..., an]
        coefficients = self.context.generate_random_coefficients(secret, poly_order)

        # Construct a polynomial function using a list of coefficents
        polynomial_funcs = CustomPolynomial(coefficients)

        # Apply this poly_funcs to each cloud identifier to a list of corresponding secret shares
        shares = [polynomial_funcs(x) for x in x_values]

        self.logging.debug(
            f"The secret [{secret}] is shared among [{nums_shares}] parties using p(x) = {str(polynomial_funcs)}")
        self.logging.debug(f"Participants  Idents: {list(x_values)}")
        self.logging.debug(f"Corresponding Shares: {shares}\n")

        if self.context.vss == 'Feldman':
            return shares, self.feldman_vss(coefficients)
        elif self.context.vss == 'Pedersen':
            return shares, self.feldman_vss(coefficients)
        else:
            return shares


if __name__ == "__main__":
    context = Context(desc="Secret Share")
    logging = context.logger
    share_engine = SecretShare(context)

    secret = 10
    nums_cloud = 10

    x_values = context.generate_random(nums=nums_cloud)

    # x_values = np.array(range(1, nums_cloud + 1))

    secret_shares = share_engine.create_shares(secret=secret,
                                               poly_order=3,
                                               nums_shares=nums_cloud,
                                               idents_shares=x_values)

    idx = context.generate_random(min=0, max=nums_cloud, nums=5)
    xs = [x_values[i] for i in idx]
    ys = [secret_shares[i] for i in idx]
    rec_secret = context.interpolate(xs, ys)

    logging.info(f"Using data {[(x, y) for x, y in zip(xs, ys)]} to recover secret [{secret}] vs [{rec_secret}]")
