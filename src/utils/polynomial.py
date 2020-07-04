from numpy.polynomial.polynomial import Polynomial


class CustomPolynomial(Polynomial):
    def __init__(self, coefficients):
        """
        input: coefficients are a list form of [a_0, a_1, ..., a_n]
        """
        self.coefficients = coefficients
        self.degree = len(self.coefficients)
        super(CustomPolynomial, self).__init__(coefficients)

    @classmethod
    def fromfilename(cls, *coefficients):
        return cls(list(coefficients))

    def __call__(self, arg):
        # TODO here is a bug for single input value
        return [int(v) for v in super(CustomPolynomial, self).__call__(arg)]

    def __str__(self):
        res = ""

        if self.coefficients[0] < 0:
            res += " - " + str(-self.coefficients[0])
        else:
            res += str(self.coefficients[0])

        for i in range(1, self.degree):
            coeff = self.coefficients[i]
            if coeff < 0:
                res += " - " + str(-coeff) + "x^" + str(i)
            else:
                res += " + " + str(coeff) + "x^" + str(i)

        return res
