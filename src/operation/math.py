# WS client example
from src.operation.op import AbstractOperation
import asyncio
import websockets
from src.share.secret_share import SecretShare
from src.event.event import MessageEvent
from src.event.message import DataMessage, ControlMessage
from src.utils.embedding import Embedding
from functools import partial
import numpy as np
import time


class MathematicalComputation(AbstractOperation):
    def __init__(self, ctx, poly_order=1):
        super(MathematicalComputation, self).__init__(ctx, poly_order)

    async def calc(self, op, op1: int = 13, op2: int = 5):
        """
        Parameters
           op:  Supported Operation [add | sub | multiply]
           op1: first operator
           op2: send operator
        """
        # The number of secret shares created for each secret.
        # It's value means how many participant servers would recieve secret share data
        nums_share = self.nums_party
        idents_share = self.party_idents[:nums_share]

        # nums_server: How many number of servers selected to recover secret data.
        # Its value is based on
        #   1. the polynomial degree that used to encode share data;
        #   2. the type of operation

        if op == self.event.type.add:
            nums_server = self.poly_order + 1
            expected = op1 + op2
            op_str = "+"
        if op == self.event.type.sub:
            nums_server = self.poly_order + 1
            expected = op1 - op2
            op_str = "-"
        if op == self.event.type.mul:
            nums_server = 2 * self.poly_order + 1
            expected = op1 * op2
            op_str = "*"
        assert nums_server <= self.nums_party

        # Create secret shares for op1
        op1_shares = self.share_engine.create_shares(secret=op1,
                                                     poly_order=self.poly_order,
                                                     nums_shares=nums_share,
                                                     idents_shares=idents_share)
        # Send shares data to all participant servers
        await self.distribute("op1", op1_shares, nums_share)

        # Create secret shares for op2
        op2_shares = self.share_engine.create_shares(secret=op2,
                                                     poly_order=self.poly_order,
                                                     nums_shares=nums_share,
                                                     idents_shares=idents_share)
        # Send shares data to all participant servers
        await self.distribute("op2", op2_shares, nums_share)

        recover_shares = await self.execute_command(op, nums_server=nums_share, nums_share=nums_share)
        result = round(self.context.interpolate(recover_shares, overflow=False), 0)

        self.logging.debug(f"Using data {recover_shares}")
        self.logging.info(
            f"Result[{op1} {op_str} {op2}]: expected {expected}, real {result}, diff {expected - result}")

    async def test_calc(self):
        await self.calc(self.event.type.sub, 15, 16)
        await self.calc(self.event.type.add, 2, 3)
        await self.calc(self.event.type.mul, 8000000000, 5600000000)