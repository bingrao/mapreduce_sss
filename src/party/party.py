import asyncio
import websockets
import ssl
from src.utils.event import MessageEvent
import numpy as np
from sage.all import *


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
        # Index of Pattern in the embedding, for example: Love, [11, 40, 47, 30]
        op2 = self.data.pop()["Value"]

        # Target, for exampel: Bob Love Alice, , size len_char * dimension
        op1 = self.data.pop()["Value"]

        # State of automation machine N0 -> N1 -> N2 -> N3 -> N4

        auto_machine = self.data.pop()["Value"]

        self.logging.debug(f"[{self.party_id}]-automation Shares Message[{len(auto_machine)}] {auto_machine}")
        self.logging.debug(f"[{self.party_id}]-op2 Shares Message[{len(op2)}] {op2}")
        self.logging.debug(f"[{self.party_id}]-op1 Shares Message[{op1.shape}] \n{op1}")
        # Transimision function for corresponding input [V0, V1, V2, V3]:
        # N4 = N3 * V3 + N4
        # N3 = N2 * V2
        # N2 = N1 * V1
        # N1 = N0 * V0
        # N0 = 1

        for index in range(op1.shape[0]):
            # auto_machine[4] = auto_machine[3] * op1[index, op2[3]] + auto_machine[4]
            # auto_machine[3] = auto_machine[2] * op1[index, op2[2]]
            # auto_machine[2] = auto_machine[1] * op1[index, op2[1]]
            # auto_machine[1] = auto_machine[0] * op1[index, op2[0]]
            account = auto_machine[-1]
            len_input = len(op2)
            for x in range(len_input):
                auto_machine[len_input-x] = auto_machine[len_input-x-1] * op1[index, op2[len_input-x-1]]
            auto_machine[-1] = auto_machine[-1] + account
            self.logging.debug(f"Party Server [{self.party_id}], input[{index}-{op1[index, ]}] transimision state {auto_machine}")

        result = auto_machine  # Return the product of array elements over a given axis.

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
