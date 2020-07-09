# WS client example
from src.operation.operation import AbstractOperation


class DataFrameComputation(AbstractOperation):
    def __init__(self, ctx, poly_order=1):
        super(DataFrameComputation, self).__init__(ctx, poly_order)
