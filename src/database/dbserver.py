# WS client example

import asyncio
import websockets
from utils.context import Context
from secret_share import SecretShare
from utils.common import generate_random, lagrange_interpolate


class DBServer:
    def __init__(self, ctx):
        self.context = ctx
        self.logging = ctx.logger
        self.partyServers = [(i, f"ws://{host}:{port}") for i, (host, port) in enumerate(ctx.partyServers[:ctx.party_size])]
        self.share_engine = SecretShare(ctx)
        self.nums_party = ctx.party_size
        self.party_idents = generate_random(nums=ctx.party_size)
        self.host, self.port = ctx.dbServer

    async def producer(self, message):

        secret = int(message)

        # Create shares for input secret
        secret_shares = self.share_engine.create_shares(secret=secret,
                                                        poly_order=3,
                                                        nums_shares=self.nums_party,
                                                        idents_shares=self.party_idents)
        recover_shares = []
        for idx, uri in self.partyServers:
            share = secret_shares[idx]
            async with websockets.connect(uri) as websocket:
                self.logging.info(f"User send message [{share}] to {uri}")

                # data sent to/(recieved from) servers must be bytes, str, or iterable
                await websocket.send(bin(share))

                greeting = await websocket.recv()  # Binary Format

                recover_shares.append((self.party_idents[idx], int(greeting, 2)))
                self.logging.info(f"User get message [{greeting}] from {uri}\n")

        self.logging.info(f"The shares {secret_shares}")
        self.logging.info(f"The recover shares {recover_shares}")

        xs = [idx for idx, _ in recover_shares]
        ys = [share for _, share in recover_shares]
        rec_secret = lagrange_interpolate(xs, ys)

        self.logging.info(f"Using data {[(x, y) for x, y in zip(xs, ys)]} to recover secret [{secret}] vs [{rec_secret}]")

    async def producer_handler(self):
        stop = False
        while not stop:
            # Get input from console as string type
            message = input("The input message: ")

            if message == 'stop':
                stop = True
            else:
                await self.producer(message)

    def start(self):
        # st

        asyncio.get_event_loop().run_until_complete(self.producer_handler())


if __name__ == "__main__":
    ctx = Context()
    client = DBServer(ctx)
    client.start()