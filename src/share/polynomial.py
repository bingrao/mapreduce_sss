from numpy.polynomial.polynomial import Polynomial
from functools import reduce


class CustomPolynomial(Polynomial):
    def __init__(self, coefficients):
        super(CustomPolynomial, self).__init__(coefficients)
        """
        input: coefficients are a list form of [a_0, a_1, ..., a_n]
        """
        # self.coef = coefficients
        self.degree = len(self.coef)

    @classmethod
    def fromfilename(cls, *coefficients):
        return cls(list(coefficients))

    def __call__(self, x):
        """
        override [[__call__]] to get better execution efficience
        """
        # return reduce(lambda a, b: a + b, map(lambda y: y[1] * (x ** y[0]), enumerate(self.coef)))
        result = 0
        for i in range(self.degree):
            result = result + self.coef[i] * (x ** i)
        return result

    def __str__(self):
        res = ""

        if self.coef[0] < 0:
            res += " - " + str(-self.coef[0])
        else:
            res += str(self.coef[0])

        for i in range(1, self.degree):
            coeff = self.coef[i]
            if coeff < 0:
                res += " - " + str(-coeff) + "x^" + str(i)
            else:
                res += " + " + str(coeff) + "x^" + str(i)

        return res
