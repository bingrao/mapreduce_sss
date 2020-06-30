class Polynomial:

    def __init__(self, coefficients):
        """ input: coefficients are a list form of [a_n, ...a_1, a_0]
        """
        self.coefficients = coefficients
        self.degree = len(self.coefficients)

    @classmethod
    def fromfilename(cls, *coefficients):
        return cls(list(coefficients))

    def __repr__(self):
        """
        method to return the canonical string representation
        of a polynomial.

        """
        return "Polynomial" + str(self.coefficients)

    # def __call__(self, x):
    #     res = 0
    #     for coeff in self.coefficients:
    #         res = res * x + coeff
    #     return res

    def __call__(self, x):
        return sum([x ** (self.degree - index - 1) * coeff for index, coeff in enumerate(self.coefficients)])

    @staticmethod
    def zip_longest(iter1, iter2, fillvalue=None):
        for i in range(max(len(iter1), len(iter2))):
            if i >= len(iter1):
                yield fillvalue, iter2[i]
            elif i >= len(iter2):
                yield iter1[i], fillvalue
            else:
                yield iter1[i], iter2[i]
            i += 1

    def __add__(self, other):
        c1 = self.coefficients[::-1]
        c2 = other.coefficients[::-1]
        res = [sum(t) for t in self.zip_longest(c1, c2, fillvalue=0)]
        return Polynomial(*res)

    def __sub__(self, other):
        c1 = self.coefficients[::-1]
        c2 = other.coefficients[::-1]

        res = [t1 - t2 for t1, t2 in self.zip_longest(c1, c2, fillvalue=0)]
        return Polynomial(*res)

    def derivative(self):
        derived_coeffs = []
        exponent = len(self.coefficients) - 1
        for i in range(len(self.coefficients) - 1):
            derived_coeffs.append(self.coefficients[i] * exponent)
            exponent -= 1
        return Polynomial(*derived_coeffs)

    def __str__(self):
        res = ""
        degree = len(self.coefficients) - 1
        res += str(self.coefficients[0]) + "x^" + str(degree)
        for i in range(1, len(self.coefficients) - 1):
            coeff = self.coefficients[i]
            if coeff < 0:
                res += " - " + str(-coeff) + "x^" + str(degree - i)
            else:
                res += " + " + str(coeff) + "x^" + str(degree - i)

        if self.coefficients[-1] < 0:
            res += " - " + str(-self.coefficients[-1])
        else:
            res += " + " + str(self.coefficients[-1])

        return res
