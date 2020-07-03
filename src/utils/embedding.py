import numpy as np


class Embedding:
    def __init__(self):
        self.alphabet_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
        self.alphabet_size = 53
        self.alphabet_vector = np.diag([1]*self.alphabet_size)

        self.numeric_list = '0123456789'
        self.numeric_size = 10
        self.numeric_vector = np.diag([1]*self.numeric_size)

    def char_to_vector(self, char: str):
        return self.alphabet_vector[self.alphabet_list.index(char)]

    @staticmethod
    def get_index(self, vec):
        idx = np.where(vec == 1)[0]
        if idx.size == 1:
            return idx[0]
        else:
            raise ValueError

    def vector_to_char(self, vec):
        return self.alphabet_list[self.get_index(vec)]

    def num_to_vector(self, num: str):
        return self.numeric_vector[self.numeric_list.index(num)]

    def vector_to_num(self, vec):
        return self.numeric_list[self.get_index(vec)]