import websockets
from src.share.secret_share import SecretShare
from src.event.event import MessageEvent
from src.event.message import DataMessage, ControlMessage
from src.utils.embedding import Embedding
from functools import partial
import numpy as np
import pandas as pd


class AbstractOperation:
    def __init__(self, ctx, poly_order: int = 1):
        self.context = ctx
        self.logging = ctx.logger
        self.zp = ctx.zp  # Finite Field
        # User choose how many participants to share data,
        # by default, a secret will be shared among all particpant servers.
        self.nums_party = self.context.config['nums_party']

        self.party_idents = ctx.generate_random(min=1, max=100, nums=self.nums_party)

        self.partyServers = [f"ws://{host}:{port}" for host, port in ctx.partyServers[:self.nums_party]]
        self.share_engine = SecretShare(ctx)
        self.poly_order = poly_order
        self.event = MessageEvent()
        self.embedding = Embedding()  # embedding layer for string or numberic

    def _load_csv_data(self, path):
        self.logging.debug(f"Load CSV file from {path}")
        return pd.read_csv(path, engine='c')

    def numeric_create_shares(self, target, poly_order, nums_share, idents_share):
        return self.share_engine.create_shares(secret=target, poly_order=poly_order,
                                               nums_shares=nums_share, idents_shares=idents_share)

    def string_create_shares(self, target, poly_order, nums_share, idents_share):
        # Partial function for shares create
        # 2D numpy arraw, size: length_string * alphabet_size
        tgt_vector = self.embedding.to_vector(target)
        tgt_vector_size = tgt_vector.shape

        # 3D numpy array, Size: length_string * alphabet_size * nums_shares
        tgt_shares_vec = np.array([self.share_engine.create_shares(secret=x,
                                                                   poly_order=poly_order,
                                                                   nums_shares=nums_share,
                                                                   idents_shares=idents_share)
                                   for x in tgt_vector.ravel()], dtype=np.int32) \
            .reshape((tgt_vector_size[0], tgt_vector_size[1], nums_share))

        # A list of 2D numpy array (size: length_string * alphabet_size) containing shares for each party servers
        # List size: nums_share
        tgt_shares = [tgt_shares_vec[:, :, [idx]].reshape(tgt_vector_size) for idx in range(nums_share)]
        if self.context.isDebug:
            self.logging.debug(f"The orignial [{target}] shares vector \n{tgt_shares_vec}")
            for idx, share in enumerate(tgt_shares):
                vec = str(tgt_vector).replace("\n", '')
                share = str(share).replace('\n', '')
                self.logging.debug(f"[{target}-{vec}]-[{idx}] distribute shares: {share}")
        return tgt_shares

    def create_shares(self, target, poly_order, nums_share, idents_share):
        if isinstance(target, str):
            return self.string_create_shares(target, poly_order, nums_share, idents_share)
        elif isinstance(target, (int, float, complex)) and not isinstance(target, bool):
            return self.numeric_create_shares(target, poly_order, nums_share, idents_share)
        else:
            raise TypeError(f"The input type [{type(target)}] does not support")

    async def distribute(self, label, secret_shares, nums_share):
        """
        Distribute secret shares to first [nums_share] selected participants
        Paramters
            label: a label name identifying the data
            secret_shares: a list of secret shares with size [[nums_share]]
            nums_share: the number of partipant servers will recieve data
        """
        if self.context.vss != 'None':
            ss_shares = secret_shares[0]
            vss_commits = secret_shares[1]
        else:
            vss_commits = None

        for idx, uri in enumerate(self.partyServers[:nums_share]):
            share = ss_shares[idx], self.party_idents[idx], vss_commits
            async with websockets.connect(uri) as websocket:
                message = self.event.serialization(DataMessage(self.event.type.data, label, share))
                # data sent to/(recieved from) servers must be bytes, str, or iterable
                await websocket.send(message)

    async def execute_command(self, op, nums_server, nums_share):
        # Send command to a specified number of participant servers
        # to conduct an operation and then recieve results from these servers.
        recover_shares = []
        for idx in self.context.generate_random(min=0, max=nums_share, nums=nums_server):
            uri = self.partyServers[idx]
            async with websockets.connect(uri) as websocket:
                message = self.event.serialization(ControlMessage(op, "Result", 0))
                self.logging.debug(f"User send message message to {uri}")
                # send the command message to a participant server and
                # switch the control to the event loop control
                await websocket.send(message)

                greeting = self.event.deserialization(await websocket.recv())
                self.logging.debug(f"User reci message from {uri}\n")

                recover_shares.append((self.party_idents[idx], greeting.value))
        return recover_shares
