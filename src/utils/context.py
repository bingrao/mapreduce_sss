from src.utils.argument import get_default_argument
from src.utils.log import get_logger
from os import makedirs
import numpy as np
from sage.all import *
import os
import warnings
from os.path import dirname, abspath, join, exists
from functools import reduce
from share.polynomial import CustomPolynomial
import numpy as np
from numpy.random import default_rng
from scipy.interpolate import lagrange
from decimal import *

BASE_DIR = dirname(dirname(abspath(__file__)))


class Context:
    def __init__(self, desc):

        assert desc == 'party' or desc == 'client' or desc == 'default'

        self.desc = desc
        # A dictionary of Config Parameters
        self.config = get_default_argument(desc=self.desc)

        self.project_dir = self.config['project_dir'] if self.config['project_dir'] != "" \
            else str(BASE_DIR)

        self.project_log = self.config["project_log"]
        if not exists(self.project_log):
            self.project_log = join(os.path.dirname(self.project_dir), 'logs', 'log.txt')
            self.create_dir(os.path.dirname(self.project_log))

        # logger interface
        self.isDebug = self.config['debug']
        self.logger = get_logger(self.desc, self.project_log, self.isDebug)

        if self.config['config'] is not None:
            with open(self.config['config']) as config_file:
                import yaml
                config_content = yaml.safe_load(config_file)
            self.partyServers = [(x['host'], x['port']) for x in config_content['servers']]

        else:
            self.partyServers = [("localhost", 8000),
                                 ("localhost", 8001),
                                 ("localhost", 8002),
                                 ("localhost", 8003),
                                 ("localhost", 8004),
                                 ("localhost", 8005),
                                 ("localhost", 8006),
                                 ("localhost", 8007),
                                 ("localhost", 8008),
                                 ("localhost", 8009)]

        self.max_nums_server = len(self.partyServers)
        if self.desc != 'client':
            self.nums_server = self.config['nums_server']
            assert self.nums_server <= self.max_nums_server

        if self.desc == 'client':
            self.nums_party = self.config['nums_party']
            assert self.nums_party <= self.max_nums_server

        self.init_rng(seed=0)
        warnings.filterwarnings('ignore')
        self.p = 2
        self.n = 12
        self.q = self.p ** self.n
        self.zp = GF(random_prime(self.q, proof=False, lbound=self.q - 3))  # Finite Field

    @staticmethod
    def init_rng(seed=0):
        np.random.seed(seed)
        # torch.random.manual_seed(seed)

    @staticmethod
    def create_dir(dir_path):
        if not exists(dir_path):
            makedirs(dir_path)

    def mapping_to_cuda(self, tensor):
        return tensor.to(self.device) if tensor is not None and self.is_cuda else tensor

    # find a number in a list
    # not find, return -1
    @staticmethod
    def find_in_list(tem, lxs):
        lenlist = len(lxs)
        ret = -1
        for x in range(lenlist):
            if lxs[x] == tem:
                ret = x
                break
        return ret

    def to_sage_integer(self, x):
        return self.zp(x)

    # generate n randome numbers, not repeated
    def generate_random_with_sage(self, n, zp):
        # numbers = self.generate_random(min=1, max=300, nums=n)
        # return numbers
        l_xs = []
        tem = zp.random_element()
        while tem == 0:
            tem = zp.random_element()
        l_xs.append(tem)
        while len(l_xs) < n:
            tem = zp.random_element()
            while tem == 0:
                tem = zp.random_element()
            if self.find_in_list(tem, l_xs) < 0:
                l_xs.append(tem)
        return l_xs

    # https://ask.sagemath.org/question/43657/list-of-random-non-zero-elements/
    # def generate_random_with_sage(nums, zp):
    #     return list(islice(filter(lambda x: x != 0, (zp.random_element() for _ in ZZ)), nums))
    @staticmethod
    def generate_random(min=1, max=100, nums=10):
        """
        Generate random and no repeated [[nums]] integers that is between [[min]] and [[max]]
        """
        rng = default_rng()
        numbers = rng.choice(np.arange(min, max), size=nums, replace=False)
        return numbers

    def generate_random_coefficients(self, secret, poly_order):
        return np.append(secret, self.generate_random(min=1, max=10, nums=poly_order))

    # We provide three different kinds of lagrange interpolate method to recover data
    # shares: [(x1, y1), (x2, y2), ..., (xn, yn)]
    @staticmethod
    def lagrange_interpolate(shares):
        xs = [idx for idx, _ in shares]
        ys = [share for _, share in shares]
        return CustomPolynomial(lagrange(xs, ys)).coef[-1]

    def interpolate(self, shares, x=0, overflow=True):
        x_values = [self.to_sage_integer(idx) if overflow else idx for idx, _ in shares]
        y_values = [share for _, share in shares]

        def _basis(j):
            p = [(x - x_values[m]) / (x_values[j] - x_values[m]) for m in range(k) if m != j]
            return reduce(np.multiply, p)

        assert len(x_values) != 0 and (len(x_values) == len(y_values)), \
            "x and y cannot be empty and must have the same length"
        k = len(x_values)
        return sum(_basis(j) * y_values[j] for j in range(k))

    # https://www.geeksforgeeks.org/implementing-shamirs-secret-sharing-scheme-in-python/
    @staticmethod
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

