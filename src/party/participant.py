import asyncio
import websockets
from utils.context import Context
import ssl
from utils.event import message_encode, message_decode, EventType
import ast
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


class ParticipantServer:
    def __init__(self, ctx, loop=None, cert_path: str = None, key_path: str = None):
        self.context = ctx
        self.logging = ctx.logger

        self.sever_id = ctx.party_id
        self.host, self.port = ctx.partyServers[self.sever_id]

        self.loop = loop if loop is not None else asyncio.new_event_loop()
        self.cert_path = cert_path
        self.key_path = key_path
        self.data = Stack()
        self.event_type = EventType()

    async def calc(self, message, websocket):
        left = self.data.pop()
        right = self.data.pop()
        if message["Type"] == self.event_type.add:
            result = left["Value"] + right["Value"]

        if message["Type"] == self.event_type.sub:
            result = left["Value"] - right["Value"]

        self.logging.info(
            f"Party Server [{self.sever_id}] recieve [{result}] from ws://{websocket._host}:{websocket._port}")

        greeting = message_encode(message["Type"], "Result", result)

        await websocket.send(greeting)
        self.logging.info(f"Message [{greeting}] is sent back to ws://{websocket._host}:{websocket._port}")

    async def multiply(self, message, websocket):
        pass

    async def match(self, message, websocket):
        # convert a string-of-list to a list
        # for example: '[[1,2],[3,2]]' --> [[1, 2], [3, 2]]
        # left = ast.literal_eval(self.data.pop()["Value"])
        left = (self.data.pop()["Value"]).astype(np.uint64)
        right = (self.data.pop()["Value"]).astype(np.uint64)
        self.logging.debug(f"[{self.sever_id}]-Left Shares Message \n{left}")
        self.logging.debug(f"[{self.sever_id}]-right Shares Message \n{right}")

        bit_wise = left * right # element-wise product
        self.logging.debug(f"[{self.sever_id}]-left bit_wise right \n{bit_wise}")

        sum_bit_wise = bit_wise.sum(axis=1) # sum of each row
        self.logging.debug(f"[{self.sever_id}]-left sum_bit_wise right {sum_bit_wise}")

        result = np.prod(sum_bit_wise, axis=0) # Return the product of array elements over a given axis.

        self.logging.info(f"Party Server [{self.sever_id}] send [{result}] to User from ws://{websocket._host}:{websocket._port}")
        await websocket.send(message_encode(message["Type"], "Result", result))

    async def count(self, message, websocket):
        pass

    async def select(self, message, websocket):
        pass

    async def join(self, message, websocket):
        pass

    async def search(self, message, websocket):
        pass

    async def consumer_handler(self, websocket, path):
        async for message in websocket:
            msg = message_decode(message)
            if msg["Type"] == self.event_type.data:
                self.data.push(msg)
                logging.info(f"Data Size {self.data.size()}, {self.data}")

            if msg["Type"] == self.event_type.add or msg["Type"] == self.event_type.sub:
                await self.calc(msg, websocket)

            if msg["Type"] == self.event_type.mul:
                await self.multiply(msg, websocket)

            if msg["Type"] == self.event_type.match:
                await self.match(msg, websocket)

            if msg["Type"] == self.event_type.count:
                await self.count(msg, websocket)

            if msg["Type"] == self.event_type.select:
                await self.select(msg, websocket)

            if msg["Type"] == self.event_type.join:
                await self.join(msg, websocket)

            if msg["Type"] == self.event_type.search:
                await self.search(msg, websocket)

    def start(self):

        if self.cert_path is not None and self.key_path is not None:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.cert_path, self.key_path)
        else:
            ssl_context = None

        self.logging.info(f"Start a participant Server ws://{self.host}:{self.port}")
        start_server = websockets.serve(self.consumer_handler, self.host, self.port, ssl=ssl_context)

        asyncio.get_event_loop().run_until_complete(start_server)
        self.logging.info("Serving. Press CTRL-C to stop.")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            self.logging.info("Websocket server stopped.")


if __name__ == "__main__":
    ctx = Context()
    logging = ctx.logger
    partyServer = ParticipantServer(ctx)
    partyServer.start()
