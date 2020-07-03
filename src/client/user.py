# WS client example

import asyncio
import websockets
from utils.context import Context
from secret_share import SecretShare
from utils.common import generate_random, lagrange_interpolate
from utils.event import message_encode, message_decode, EventType
from utils.embedding import Embedding


class UserClient:
    def __init__(self, ctx):
        self.context = ctx
        self.logging = ctx.logger
        self.nums_party = ctx.party_size
        self.party_idents = generate_random(nums=self.nums_party)
        self.partyServers = [f"ws://{host}:{port}" for host, port in ctx.partyServers[:self.nums_party]]
        self.share_engine = SecretShare(ctx)
        self.host, self.port = ctx.userClient
        self.poly_order = 1
        self.event_type = EventType()
        self.embedding = Embedding()

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

                self.logging.info(f"User send message [{message}] to {uri}")
                # data sent to/(recieved from) servers must be bytes, str, or iterable
                await websocket.send(message)

                greeting = message_decode(await websocket.recv())  # Binary Format

                recover_shares.append((self.party_idents[idx], int(greeting["Value"], 2)))
                self.logging.info(f"User reci message [{greeting}] from {uri}\n")

        xs = [idx for idx, _ in recover_shares]
        ys = [share for _, share in recover_shares]
        rec_secret = lagrange_interpolate(xs, ys)

        self.logging.info(
            f"Using data {[(x, y) for x, y in zip(xs, ys)]} to recover secret [{right} {op} {left}] vs [{rec_secret}]")

    async def distribute(self, label, secret_shares):
        for idx, uri in enumerate(self.partyServers):
            share = secret_shares[idx]
            async with websockets.connect(uri) as websocket:
                message = message_encode(self.event_type.data, label, share)
                # data sent to/(recieved from) servers must be bytes, str, or iterable
                await websocket.send(message)
                self.logging.info(f"User send message [{message}] to {uri}")

    async def producer_handler(self):
        await self.calc(self.event_type.sub, 15, 16)
        await self.calc(self.event_type.add, 2, 3)

    def start(self):
        # self.logging.info(f"Start an User Server ws://{self.host}:{self.port}")
        # start_server = websockets.serve(self.producer_handler, self.host, self.port)
        # asyncio.get_event_loop().run_until_complete(start_server)

        asyncio.get_event_loop().run_until_complete(self.producer_handler())


if __name__ == "__main__":
    ctx = Context()
    client = UserClient(ctx)
    client.start()
