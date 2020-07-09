# WS client example
from src.operation.math import MathematicalComputation
from src.operation.string import StringComputation
from collections import ChainMap
import numpy as np
import pandas as pd


class DataFrameComputation(MathematicalComputation, StringComputation):
    def __init__(self, ctx, poly_order=1):
        super(DataFrameComputation, self).__init__(ctx, poly_order)
        # self.data_df =

    def category_attr_label_encode(self, data_input, nums_limit=10):
        """
        Find category attributes and label encode (Using number index replace of string content)
        """
        data = data_input if data_input is not None else self._load_csv_data(self.context.config['data'])
        metadata = {}
        for col in data.columns.values:
            if data.dtypes[col] == np.object:
                cat_index = pd.CategoricalIndex(data[col])
                if cat_index.categories.size <= nums_limit:
                    data[col] = cat_index.codes
                    metadata[col] = dict(ChainMap(*map(lambda x: {x[1]: x[0]}, enumerate(cat_index.categories))))
        return data, metadata

    @staticmethod
    def preprocess(data_input):
        pass

    @staticmethod
    def postprocess():
        pass
