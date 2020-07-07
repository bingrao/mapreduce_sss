# WS client example

import asyncio
import websockets
from src.utils.secret_share import SecretShare
from src.utils.common import generate_random, lagrange_interpolate
from src.utils.event import MessageEvent
from src.utils.embedding import Embedding
from functools import partial
import numpy as np


class UserClient:
    def __init__(self, ctx, poly_order=1):
        self.context = ctx
        self.logging = ctx.logger

        # User choose how many participants to share data,
        # by default, a secret will be shared among all particpant servers.
        self.nums_party = self.context.config['nums_party']

        # self.party_idents = generate_random(nums=self.nums_party)
        self.party_idents = np.array(range(1, self.nums_party + 1))

        self.partyServers = [f"ws://{host}:{port}" for host, port in ctx.partyServers[:self.nums_party]]
        self.share_engine = SecretShare(ctx)
        self.poly_order = poly_order
        self.event = MessageEvent()
        self.embedding = Embedding()  # embedding layer for string or numberic

    async def execute_command(self, op, nums_server):
        # Send command to a specified number of participant servers
        # to conduct an operation and then recieve results from these servers.
        recover_shares = []
        for idx in generate_random(min=0, max=self.nums_party, nums=nums_server):
            uri = self.partyServers[idx]
            async with websockets.connect(uri) as websocket:
                """
                data sent to/(recieved from) servers must be bytes, str, or iterable
                """
                message = self.event.serialization(op, "Result", 0)
                self.logging.debug(f"User send message message to {uri}")
                await websocket.send(message)

                greeting = self.event.deserialization(await websocket.recv())
                self.logging.debug(f"User reci message from {uri}\n")

                recover_shares.append((self.party_idents[idx], greeting["Value"]))
        return recover_shares

    async def count(self, op, op1, op2):
        """
        Paramters:
            -op: count operation
            -op1: target string, for example: ALice Love Bob!
            -op2: Search Pattern, for example: Love
        """
        assert len(op1) >= len(op2), f"Constraint Condition: len[{op1}] >= len[{op2}] does not match"

        nums_server = len(op2) + 1
        expected = op1.count(op2)
        op_str = "count"

        assert nums_server <= self.nums_party, \
            f"Recover {op1, op2} need at least {nums_server} servers (<= {self.nums_party})"

        func_shares = partial(self.share_engine.create_shares,
                              nums_shares=self.nums_party,
                              idents_shares=self.party_idents)

        # ********************** State autormation machine
        automation_machine = np.zeros(len(op2) + 1, dtype=np.int)  # Initial statement
        automation_machine[0] = 1

        automation_shares_vec = np.array([func_shares(secret=x, poly_order=idx + 2)
                                          for idx, x in enumerate(automation_machine.ravel())]) \
            .reshape((automation_machine.size, self.nums_party))

        automation_shares = automation_shares_vec.transpose()  # nums_party * nums_node

        await self.distribute("state", automation_shares)
        if self.context.isDebug:
            self.logging.debug(f"The orignial automation shares vector \n{automation_shares}")

        # ********************** First Operator
        op1_vector = self.embedding.str_to_vector(op1)
        op1_vector_size = op1_vector.shape

        # Size (length_string * alphabet_size * nums_shares)
        op1_shares_vec = np.array([func_shares(secret=x, poly_order=self.poly_order) for x in op1_vector.ravel()],
                                  dtype=np.int32).reshape((op1_vector_size[0], op1_vector_size[1], self.nums_party))

        op1_shares = [op1_shares_vec[:, :, [idx]].reshape(op1_vector_size) for idx in range(self.nums_party)]

        if self.context.isDebug:
            self.logging.debug(f"The orignial op1 shares vector \n{op1_shares_vec}")
            for idx, share in enumerate(op1_shares):
                vec = str(op1_vector).replace("\n", '')
                share = str(share).replace('\n', '')
                self.logging.debug(f"op1-[{op1}-{vec}]-[{idx}] distribute shares: {share}")

        await self.distribute("op1", op1_shares)

        # ********************** Second operator
        op2_index = np.array([self.embedding.alphabet_list.index(char) for char in op2])
        op2_dist = np.tile(op2_index, self.nums_party).reshape((self.nums_party, op2_index.size))
        await self.distribute("op2", op2_dist)

        if self.context.isDebug:
            self.logging.debug(f"The orignial op2 shares vector \n{op2_dist}")
            for idx, share in enumerate(op2_dist):
                share = str(share).replace('\n', '')
                self.logging.debug(f"op1-[{op2}]-[{idx}] distribute shares: {share}")

        recover_shares = await self.execute_command(op, self.nums_party)

        result = []
        for index in range(len(op2) + 1):
            node_state = [(ident, reg[index]) for ident, reg in recover_shares]
            node_value = lagrange_interpolate(node_state)
            result.append(round(node_value, 2))

        self.logging.debug(f"Using data {recover_shares}")
        self.logging.info(
            f"Result[{op1} {op_str} {op2}]: expected {expected}, real {result}")

    async def match(self, op, op1, op2):
        assert len(op1) == len(op2), f"The lenght of [{op1}] and [{op2}] does not match"

        nums_server = 2 * len(op1) + 1
        # nums_server = self.nums_party
        expected = 1.0 if op1 == op2 else 0.0
        op_str = "=="
        assert nums_server <= self.nums_party, \
            f"Recover {op1, op2} need at least {nums_server} servers (<= {self.nums_party})"

        op1_vector = self.embedding.str_to_vector(op1)
        op1_vector_size = op1_vector.shape
        op2_vector = self.embedding.str_to_vector(op2)
        op2_vector_size = op2_vector.shape

        func_shares = partial(self.share_engine.create_shares,
                              poly_order=self.poly_order,
                              nums_shares=self.nums_party,
                              idents_shares=self.party_idents)

        # Size (length_string * alphabet_size * nums_shares)
        op1_shares_vec_tmp = np.array([func_shares(x) for x in op1_vector.ravel()], dtype=np.int32)

        op1_shares_vec = op1_shares_vec_tmp.reshape((op1_vector_size[0], op1_vector_size[1], self.nums_party))

        op1_shares = [op1_shares_vec[:, :, [idx]].reshape(op1_vector_size) for idx in range(self.nums_party)]

        if self.context.isDebug:
            self.logging.debug(f"The orignial op1 shares vector \n{op1_shares_vec}")
            for idx, share in enumerate(op1_shares):
                vec = str(op1_vector).replace("\n", '')
                share = str(share).replace('\n', '')
                self.logging.debug(f"op1-[{op1}-{vec}]-[{idx}] distribute shares: {share}")

        # Size (length_string * alphabet_size * nums_shares)
        op2_shares_vec = np.array([func_shares(x) for x in op2_vector.ravel()],
                                  dtype=np.int32).reshape((op2_vector_size[0], op2_vector_size[1], self.nums_party))

        op2_shares = [op2_shares_vec[:, :, [idx]].reshape(op2_vector_size) for idx in range(self.nums_party)]

        if self.context.isDebug:
            self.logging.debug(f"The orignial op2 shares vector \n{op2_shares_vec}")
            for idx, share in enumerate(op2_shares):
                vec = str(op2_vector).replace("\n", '')
                share = str(share).replace('\n', '')
                self.logging.debug(f"op2-[{op2}-{vec}]-[{idx}] distribute shares: {share}")

        await self.distribute("op1", op1_shares)

        await self.distribute("op2", op2_shares)

        recover_shares = await self.execute_command(op, nums_server)

        result = lagrange_interpolate(recover_shares)

        self.logging.debug(f"Using data {recover_shares}")
        self.logging.info(
            f"Result[{op1} {op_str} {op2}]: expected {expected}, real {round(result, 2)}, diff {round(expected - result, 2)}")

    async def calc(self, op, op1=13, op2=5):
        """
        Parameters
           op:  Supported Operation [add | sub | multiply]
           op1: first operator
           op2: send operator
        """

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
                                                     nums_shares=self.nums_party,
                                                     idents_shares=self.party_idents)
        # Send shares data to all participant servers
        await self.distribute("op1", op1_shares)

        # Create secret shares for op2
        op2_shares = self.share_engine.create_shares(secret=op2,
                                                     poly_order=self.poly_order,
                                                     nums_shares=self.nums_party,
                                                     idents_shares=self.party_idents)
        # Send shares data to all participant servers
        await self.distribute("op2", op2_shares)

        recover_shares = await self.execute_command(op, nums_server)
        result = lagrange_interpolate(recover_shares)

        self.logging.debug(f"Using data {recover_shares}")
        self.logging.info(
            f"Result[{op1} {op_str} {op2}]: expected {expected}, real {round(result, 2)}, diff {round(expected - result, 2)}")

    async def distribute(self, label, secret_shares):
        """
        Distribute secret shares to all selected participants
        Paramters
            label: a label name identifying the data
            secret_shares: a list of secret shares
        """
        for idx, uri in enumerate(self.partyServers):
            share = secret_shares[idx]
            async with websockets.connect(uri) as websocket:
                message = self.event.serialization(self.event.type.data, label, share)
                # data sent to/(recieved from) servers must be bytes, str, or iterable
                await websocket.send(message)

    async def test_calc(self):
        await self.calc(self.event.type.sub, 15, 16)
        await self.calc(self.event.type.add, 2, 3)
        await self.calc(self.event.type.mul, 8, 56)

    async def test_match(self):
        from functools import reduce
        nums_str = 3
        for i in range(self.embedding.alphabet_size):
            xs = reduce(lambda x, y: x + y, [self.embedding.alphabet_list[i] for i in
                                             generate_random(min=0, max=self.embedding.alphabet_size, nums=nums_str)])
            ys = reduce(lambda x, y: x + y, [self.embedding.alphabet_list[i] for i in
                                             generate_random(min=0, max=self.embedding.alphabet_size, nums=nums_str)])
            await self.match(self.event.type.match, xs, ys)
            await self.match(self.event.type.match, xs, xs)
            await self.match(self.event.type.match, ys, ys)

    async def producer_handler(self):
        # await self.test_match()
        # await self.test_calc()
        await self.count(self.event.type.count, 'ABCD', 'ABCD')
        # await self.match(self.event.type.match, "ABC", "BBC")

    def start(self):
        asyncio.get_event_loop().run_until_complete(self.producer_handler())
