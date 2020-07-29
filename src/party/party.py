import asyncio
import websockets
import ssl
from src.event.event import MessageEvent
from src.event.message import Message
from sage.all import *
import numpy as np


def sage_matrix_elementwise(M, N):
    assert(M.parent() == N.parent())

    nc, nr = M.ncols(), M.nrows()
    A = copy(M.parent().zero())

    for r in range(nr):
        for c in range(nc):
            A[r, c] = M[r, c] * N[r, c]
    return A


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

    def _load_data(self, name=None):
        return self.data.pop()

    def _save_data(self, message):
        share, ident, commits = message.value

        if self.context.vss == 'Feldman' and commits is not None:
            self.logging.debug(f"Server[{self.party_id}-{ident}] holds Share [{share}] with commits {commits}, "
                              f"p={self.context.p}, g={self.context.g}")
            share_vss = self.context.g ** Integer(share) % self.context.p
            commits_vss = prod([commit ** (ident ** i) for i, commit in enumerate(commits)]) % self.context.p
            assert share_vss == commits_vss, f"Server[{self.party_id}-{ident}] share_vss [{share_vss}] == commits_vss [{commits_vss}]"
        elif self.context.vss == 'Pedersen' and commits is not None:
            self.logging.debug(f"Server[{self.party_id}-{ident}] holds Share [{share}] with commits {commits}, "
                               f"p={self.context.p}, g={self.context.g}")
            share_vss = self.context.g ** Integer(share) % self.context.p
            commits_vss = prod([commit ** (ident ** i) for i, commit in enumerate(commits)]) % self.context.p
            assert share_vss == commits_vss, f"Server[{self.party_id}-{ident}] share_vss [{share_vss}] == commits_vss [{commits_vss}]"
        else:
            pass
        self.data.push(message)

    async def calc(self, message, websocket):
        op2 = self._load_data().value[0]
        op1 = self._load_data().value[0]
        if message.msgType == self.event.type.add:
            result = op1 + op2

        if message.msgType == self.event.type.sub:
            result = op1 - op2

        if message.msgType == self.event.type.mul:
            result = op1 * op2

        greeting = self.event.serialization(Message(message.msgType, "Result", result))

        # Send intermediate results to User
        await websocket.send(greeting)

    async def match(self, message, websocket):

        # Using Sage Math Matrix to overcome data overflow issue
        # Numpy and python int does not support data overflow issue
        op2 = self.data.pop().value  # Numpy-Style, size: length_string * alphabet_size
        op1 = self.data.pop().value  # Numpy-Style, size: length_string * alphabet_size

        # op2 = matrix(self._load_data().value)  # size: length_string * alphabet_size
        # op1 = matrix(self._load_data().value)  # size: length_string * alphabet_size

        self.logging.debug(f"[{self.party_id}]-op1 Shares Message \n{op1}")
        self.logging.debug(f"[{self.party_id}]-op2 Shares Message \n{op2}")

        bit_wise = op1 * op2  # Numpy-Style element-wise product
        # bit_wise = sage_matrix_elementwise(op1, op2)  # Sage-Style element-wise product
        self.logging.debug(f"[{self.party_id}]-op1 bit_wise op2 \n{bit_wise}")

        sum_bit_wise = bit_wise.sum(axis=1)  # Numpy-Style sum of each row
        # sum_bit_wise = sum(bit_wise.columns())  # Sage-Style sum of each row
        self.logging.debug(f"[{self.party_id}]-op1 sum_bit_wise op2 {sum_bit_wise}")

        # Return the product of array elements over a given axis.
        # Here prod and element are used Sage built-in functions and type (IntegerMod_Int)
        # to git rid of data overflow issues resulted from a butch of integer's multipication.
        result = prod([self.context.to_sage_integer(x) for x in sum_bit_wise])

        self.logging.debug(
            f"Party Server [{self.party_id}] send [{result}] to User from ws://{websocket._host}:{websocket._port}")
        await websocket.send(self.event.serialization(Message(message.msgType, "Result", result)))

    async def string_count(self, message, websocket):
        # 1D-numpy array, size len_char
        # Index of Pattern in the embedding, for example: Love, [11, 40, 47, 30]
        op2 = self._load_data().value

        # 2D-numpy array Target, size len_char * dimension
        # for exampel: Bob Love Alice
        op1 = self._load_data().value

        # 1D-numpy array, size len_char + 1
        # State of automation machine N0 -> N1 -> N2 -> N3 -> ... -> N4
        auto_machine = [self.context.to_sage_integer(x) for x in self._load_data().value]

        self.logging.debug(f"[{self.party_id}]-automation Shares Message[{len(auto_machine)}] {auto_machine}")
        self.logging.debug(f"[{self.party_id}]-op2 Shares Message[{op2.shape}] {op2}")
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

            prev_account = auto_machine[-1]
            # 3, 2, 1, 0, reversed order to make sure to
            # use previous state in automation machine
            for x in reversed(range(op2.size)):
                auto_machine[x + 1] = auto_machine[x] * op1[index, op2[x]]
            auto_machine[-1] = auto_machine[-1] + prev_account

            self.logging.debug(f"Party Server [{self.party_id}], input[{index}-{op1[index,]}] "
                               f"transimision state {auto_machine}")

        result = auto_machine  # Return the product of array elements over a given axis.

        self.logging.debug(
            f"Party Server [{self.party_id}] send [{result}] to User from ws://{websocket._host}:{websocket._port}")

        await websocket.send(self.event.serialization(Message(message.msgType, "Result", result)))

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
            msg = self.event.deserialization(message)
            if msg.msgType == self.event.type.data:
                self._save_data(msg)

            if msg.msgType == self.event.type.add \
                    or msg.msgType == self.event.type.sub \
                    or msg.msgType == self.event.type.mul:
                await self.calc(msg, websocket)

            if msg.msgType == self.event.type.match:
                await self.match(msg, websocket)

            if msg.msgType == self.event.type.count:
                await self.count(msg, websocket)

            if msg.msgType == self.event.type.string_count:
                await self.string_count(msg, websocket)

            if msg.msgType == self.event.type.select:
                await self.select(msg, websocket)

            if msg.msgType == self.event.type.join:
                await self.join(msg, websocket)

            if msg.msgType == self.event.type.search:
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
