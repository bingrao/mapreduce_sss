# WS client example

import asyncio
import time
from src.operation.math import MathematicalComputation
from src.operation.string import StringComputation
from src.operation.dataframe import DataFrameComputation


class UserClient:
    def __init__(self, ctx, poly_order=1):
        self.context = ctx
        self.logging = ctx.logger
        self.math_op = MathematicalComputation(ctx, poly_order)
        self.str_op = StringComputation(ctx, poly_order)
        self.df_op = DataFrameComputation(ctx, poly_order)

    async def producer_handler(self):

        start = time.time()

        await self.str_op.test_match()
        await self.math_op.test_calc()
        await self.str_op.aa_count_sage_standalone()
        await self.str_op.string_count(self.event.type.string_count, 'Bob Love ALice', 'L')
        await self.str_op.match(self.event.type.match, "ABCed", "ABCed")

        end = time.time()
        self.logging.info(f"The execution time {end - start}")

    def start(self):
        asyncio.get_event_loop().run_until_complete(self.producer_handler())
