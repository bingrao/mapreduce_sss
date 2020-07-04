# WS client example

import asyncio
import websockets
from utils.context import Context
from secret_share import SecretShare
from utils.common import generate_random, lagrange_interpolate
from utils.event import message_encode, message_decode, EventType
from utils.embedding import Embedding
from functools import partial
import numpy as np

class UserClient:
    def __init__(self, ctx):
        self.context = ctx
        self.logging = ctx.logger
        self.nums_party = self.context.config['nums_party']

        # self.party_idents = generate_random(nums=self.nums_party)
        self.party_idents = np.array(range(1, self.nums_party + 1))

        self.partyServers = [f"ws://{host}:{port}" for host, port in ctx.partyServers[:self.nums_party]]
        self.share_engine = SecretShare(ctx)
        self.poly_order = 1
        self.event_type = EventType()
        self.embedding = Embedding()

    async def match(self, op, left, right):
        assert len(left) == len(right)

        length = 2*len(left) + 1

        left_vector = self.embedding.str_to_vector(left)
        left_vector_size = left_vector.shape
        right_vector = self.embedding.str_to_vector(right)
        right_vector_size = right_vector.shape

        func_shares = partial(self.share_engine.create_shares,
                              poly_order=self.poly_order,
                              nums_shares=self.nums_party,
                              idents_shares=self.party_idents)

        # Size (length_string * alphabet_size * nums_shares)
        left_shares_vec = np.array([func_shares(x) for x in left_vector.ravel()],
                                   dtype=np.int32).reshape((left_vector_size[0],left_vector_size[1],self.nums_party))

        left_shares = [left_shares_vec[:, :, [idx]].reshape(left_vector_size) for idx in range(self.nums_party)]

        if self.context.isDebug:
            self.logging.debug(f"The orignial left shares vector \n{left_shares_vec}")
            for idx, share in enumerate(left_shares):
                vec = str(left_vector).replace("\n", '')
                share = str(share).replace('\n', '')
                self.logging.debug(f"Left-[{left}-{vec}]-[{idx}] distribute shares: {share}")

        # Size (length_string * alphabet_size * nums_shares)
        right_shares_vec = np.array([func_shares(x) for x in right_vector.ravel()],
                                    dtype=np.int32).reshape((right_vector_size[0],right_vector_size[1],self.nums_party))

        right_shares = [right_shares_vec[:, :, [idx]].reshape(right_vector_size) for idx in range(self.nums_party)]

        if self.context.isDebug:
            self.logging.debug(f"The orignial right shares vector \n{right_shares_vec}")
            for idx, share in enumerate(right_shares):
                vec = str(right_vector).replace("\n", '')
                share = str(share).replace('\n', '')
                self.logging.debug(f"Right-[{right}-{vec}]-[{idx}] distribute shares: {share}")

        await self.distribute("x", left_shares)

        await self.distribute("x", right_shares)

        recover_shares = []
        for idx, uri in enumerate(self.partyServers):
            async with websockets.connect(uri) as websocket:
                message = message_encode(op, "Result", 0)

                self.logging.debug(f"User send message message to {uri}")
                # data sent to/(recieved from) servers must be bytes, str, or iterable
                await websocket.send(message)

                greeting = message_decode(await websocket.recv())  # String Format

                recover_shares.append((self.party_idents[idx], greeting["Value"]))
                self.logging.debug(f"User reci message [{greeting}] from {uri}\n")

        xs = [idx for idx, _ in recover_shares[:length]]
        ys = [share for _, share in recover_shares[:length]]
        rec_secret = lagrange_interpolate(xs, ys)

        self.logging.info(
            f"Recover secret [{right} {op} {left}] vs [{rec_secret}] Using data {[(x, y) for x, y in zip(xs, ys)]}")

    async def calc(self, op, left=13, right=5):

        # Create shares for input secret
        secret_shares_x = self.share_engine.create_shares(secret=left,
                                                          poly_order=self.poly_order,
                                                          nums_shares=self.nums_party,
                                                          idents_shares=self.party_idents)
        await self.distribute("x", secret_shares_x)

        # Create shares for input secret
        secret_shares_y = self.share_engine.create_shares(secret=right,
                                                          poly_order=self.poly_order,
                                                          nums_shares=self.nums_party,
                                                          idents_shares=self.party_idents)
        await self.distribute("y", secret_shares_y)

        recover_shares = []
        for idx, uri in enumerate(self.partyServers):
            async with websockets.connect(uri) as websocket:
                message = message_encode(op, "Result", 0)

                self.logging.debug(f"User send message message to {uri}")
                # data sent to/(recieved from) servers must be bytes, str, or iterable
                await websocket.send(message)

                greeting = message_decode(await websocket.recv())  # Binary Format

                recover_shares.append((self.party_idents[idx], greeting["Value"]))
                self.logging.debug(f"User reci message [{greeting}] from {uri}\n")

        xs = [idx for idx, _ in recover_shares]
        ys = [share for _, share in recover_shares]
        rec_secret = lagrange_interpolate(xs, ys)

        self.logging.info(
            f"Recover secret [{right} {op} {left}] vs [{rec_secret}] Using data {[(x, y) for x, y in zip(xs, ys)]}")

    async def distribute(self, label, secret_shares):
        for idx, uri in enumerate(self.partyServers):
            share = secret_shares[idx]
            async with websockets.connect(uri) as websocket:
                message = message_encode(self.event_type.data, label, share)
                # data sent to/(recieved from) servers must be bytes, str, or iterable
                await websocket.send(message)

    async def producer_handler(self):
        # await self.calc(self.event_type.sub, 15, 16)
        # await self.calc(self.event_type.add, 2, 3)
        await self.match(self.event_type.match, "DCAB", "DCAB")

    def start(self):
        # self.logging.info(f"Start an User Server ws://{self.host}:{self.port}")
        # start_server = websockets.serve(self.producer_handler, self.host, self.port)
        # asyncio.get_event_loop().run_until_complete(start_server)

        asyncio.get_event_loop().run_until_complete(self.producer_handler())