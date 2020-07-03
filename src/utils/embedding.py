import numpy as np


class Embedding:
    def __init__(self):
        # self.alphabet_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
        self.alphabet_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
        self.alphabet_size = len(self.alphabet_list)
        self.alphabet_vector = np.diag([1]*self.alphabet_size)

        self.numeric_list = '0123456789'
        self.numeric_size = len(self.numeric_list)
        self.numeric_vector = np.diag([1]*self.numeric_size)

    def str_to_vector(self, string: str):
        index = [self.alphabet_list.index(char) for char in string]
        return self.alphabet_vector[index, ]

    def nums_to_vector(self, nums: str):
        index = [self.numeric_list.index(n) for n in nums]
        return self.numeric_vector[index, ]

    @staticmethod
    def nums_to_binary(self, nums):
        return bin(int(nums))

    @staticmethod
    def get_index(self, vec):
        idx = np.where(vec == 1)[0]
        if idx.size == 1:
            return idx[0]
        else:
            raise ValueError

    def vector_to_char(self, vec):
        return self.alphabet_list[self.get_index(vec)]

    def vector_to_num(self, vec):
        return self.numeric_list[self.get_index(vec)]