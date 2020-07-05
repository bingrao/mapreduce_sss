import asyncio
import websockets
import ssl
from src.utils.event import MessageEvent

import numpy as np


# A simple class stack that only allows pop and push operations
class Stack:

    def __init__(self):
        self.stack = []

    def pop(self):
        if len(self.stack) < 1:
            return None
        return self.stack.pop()

    def peek(self):
        return self.stack[0]

    def push(self, item):
        self.stack.append(item)

    def size(self):
        return len(self.stack)

    def __len__(self):
        return self.size()


class PartyServer:
    def __init__(self, ctx, party_id, cert_path: str = None, key_path: str = None):
        self.context = ctx
        self.logging = ctx.logger
        self.party_id = party_id
        self.host, self.port = ctx.partyServers[self.party_id]
        self.cert_path = cert_path
        self.key_path = key_path
        self.data = Stack()
        self.event = MessageEvent()

    async def calc(self, message, websocket):
        op2 = self.data.pop()
        op1 = self.data.pop()
        if message["Type"] == self.event.type.add:
            result = op1["Value"] + op2["Value"]

        if message["Type"] == self.event.type.sub:
            result = op1["Value"] - op2["Value"]

        if message["Type"] == self.event.type.mul:
            result = op1["Value"] * op2["Value"]

        greeting = self.event.serialization(message["Type"], "Result", result)

        # Send intermediate results to User
        await websocket.send(greeting)

    async def match(self, message, websocket):
        op2 = (self.data.pop()["Value"]).astype(np.uint64)
        op1 = (self.data.pop()["Value"]).astype(np.uint64)
        self.logging.debug(f"[{self.party_id}]-op1 Shares Message \n{op1}")
        self.logging.debug(f"[{self.party_id}]-op2 Shares Message \n{op2}")

        bit_wise = op1 * op2  # element-wise product
        self.logging.debug(f"[{self.party_id}]-op1 bit_wise op2 \n{bit_wise}")

        sum_bit_wise = bit_wise.sum(axis=1)  # sum of each row
        self.logging.debug(f"[{self.party_id}]-op1 sum_bit_wise op2 {sum_bit_wise}")

        result = np.prod(sum_bit_wise, axis=0)  # Return the product of array elements over a given axis.

        self.logging.debug(
            f"Party Server [{self.party_id}] send [{result}] to User from ws://{websocket._host}:{websocket._port}")
        await websocket.send(self.event.serialization(message["Type"], "Result", result))

    async def count(self, message, websocket):
        # Pattern, for example: Love, size len_char * dimension
        op2 = (self.data.pop()["Value"]).astype(np.uint64)

        # Target, for exampel: Bob Love Alice, , size len_char * dimension
        op1 = (self.data.pop()["Value"]).astype(np.uint64)

        self.logging.debug(f"[{self.party_id}]-op1 Shares Message \n{op1}")
        self.logging.debug(f"[{self.party_id}]-op2 Shares Message \n{op2}")

        bit_wise = op1 * op2  # element-wise product
        self.logging.debug(f"[{self.party_id}]-op1 bit_wise op2 \n{bit_wise}")

        sum_bit_wise = bit_wise.sum(axis=1)  # sum of each row
        self.logging.debug(f"[{self.party_id}]-op1 sum_bit_wise op2 {sum_bit_wise}")

        result = np.prod(sum_bit_wise, axis=0)  # Return the product of array elements over a given axis.

        self.logging.debug(
            f"Party Server [{self.party_id}] send [{result}] to User from ws://{websocket._host}:{websocket._port}")
        await websocket.send(self.event.serialization(message["Type"], "Result", result))

    async def select(self, message, websocket):
        pass

    async def join(self, message, websocket):
        pass

    async def search(self, message, websocket):
        pass

    async def consumer_handler(self, websocket, path):
        async for message in websocket:
            msg = self.event.deserialization(message)
            if msg["Type"] == self.event.type.data:
                self.data.push(msg)

            if msg["Type"] == self.event.type.add \
                    or msg["Type"] == self.event.type.sub \
                    or msg["Type"] == self.event.type.mul:
                await self.calc(msg, websocket)

            if msg["Type"] == self.event.type.match:
                await self.match(msg, websocket)

            if msg["Type"] == self.event.type.count:
                await self.count(msg, websocket)

            if msg["Type"] == self.event.type.select:
                await self.select(msg, websocket)

            if msg["Type"] == self.event.type.join:
                await self.join(msg, websocket)

            if msg["Type"] == self.event.type.search:
                await self.search(msg, websocket)

    def start(self):

        if self.cert_path is not None and self.key_path is not None:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.cert_path, self.key_path)
        else:
            ssl_context = None

        self.logging.info(f"[{self.party_id}]-Start a participant Server ws://{self.host}:{self.port}")
        start_server = websockets.serve(self.consumer_handler, self.host, self.port, ssl=ssl_context)

        asyncio.get_event_loop().run_until_complete(start_server)
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            self.logging.info("Websocket server stopped.")
