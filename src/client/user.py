# WS client example

import asyncio
import websockets
from share.secret_share import SecretShare
from event.event import MessageEvent
from src.utils.embedding import Embedding
from functools import partial
import numpy as np
import time


class UserClient:
    def __init__(self, ctx, poly_order=1):
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

    def create_shares(self, target, poly_order, nums_share, idents_share):

        # Partial function for shares create
        func_shares = partial(self.share_engine.create_shares,
                              poly_order=poly_order,
                              nums_shares=nums_share,
                              idents_shares=idents_share)
        # 2D numpy arraw, size: length_string * alphabet_size
        tgt_vector = self.embedding.to_vector(target)
        tgt_vector_size = tgt_vector.shape

        # 3D numpy array, Size: length_string * alphabet_size * nums_shares
        tgt_shares_vec = np.array([func_shares(x) for x in tgt_vector.ravel()], dtype=np.int32) \
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

    async def execute_command(self, op, nums_server, nums_share):
        # Send command to a specified number of participant servers
        # to conduct an operation and then recieve results from these servers.
        recover_shares = []
        for idx in self.context.generate_random(min=0, max=nums_share, nums=nums_server):
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

    async def aa_count_sage_standalone(self, op1='ABCD', op2='ABCD'):
        self.logging.info(f"The finite filed we are using: Zp={self.zp}")
        self.logging.info(f"cloud numbers: {len(self.party_idents)}")
        self.logging.info(f"x values for each cloud: {self.party_idents}")

        # input one file to share
        FiletoBestored = op1.strip()
        self.logging.info(f"file stream to be searched: {FiletoBestored}")

        # for temporary store vector
        l_Filshares = []
        # for one file in one cloud, one row for one cloud. (for example 10 clouds)
        # in each row, every cell for one alphabet (for example each cell consists of 53 elements)

        for x in range(self.nums_party):
            l_Filshares.append([])

        x = FiletoBestored[0]
        vector = self.embedding.to_vector(x)[0]  # Get a vector representation for a char x
        self.logging.info(f"The char [{x}] --> {vector}")

        l_y_vectorshares = []  # for one vector,or for one symbol
        for xx in range(self.nums_party):
            l_y_vectorshares.append([])

        for x in FiletoBestored:
            vector = self.embedding.to_vector(x)[0]  # Get a vector representation for a char x

            # secret share each vector
            l_y_vectorshares = []  # for one vector,or for one symbol
            for xx in range(self.nums_party):
                l_y_vectorshares.append([])

            for y in vector:
                shares = self.share_engine.create_shares(secret=y, poly_order=1, nums_shares=self.nums_party,
                                                         idents_shares=self.party_idents)
                for xx in range(self.nums_party):
                    l_y_vectorshares[xx].append(shares[xx])

            # send to clouds
            # transfer data in l_y_vectorshares to l_Filshares
            for xx in range(self.nums_party):
                l_Filshares[xx].append(l_y_vectorshares[xx])

        self.logging.info(
            f"len(l_Filshares) = {len(l_Filshares)}, len(l_Filshares[0]) = {len(l_Filshares[0])}, "
            f"len(l_Filshares[0][0]) = {len(l_Filshares[0][0])}")

        self.logging.info(f"l_Filshares[0][0]: {l_Filshares[0][0]}")

        self.logging.info('distribute file ending...')
        self.logging.info('-----------------------------------')

        self.logging.info('Generate AA now')

        n_node = len(op2) + 1
        l_Node = [1 if x == 0 else 0 for x in range(n_node)]
        l_NodesharesforC = []

        # set positon for the word 'Love'
        op2_index = [self.embedding.alphabet_list.index(char) for char in op2]

        # set initial cell for self.nums_party clouds
        for xx in range(self.nums_party):
            l_NodesharesforC.append([])

        # secret share AA
        # each share for x cloud is stored in l_NodesharesforC[x]
        for i in range(n_node):
            # shares = secretshare(l_Node[i], self.nums_party, i + 2, l_xs)
            shares = self.share_engine.create_shares(secret=l_Node[i], poly_order=i + 2, nums_shares=self.nums_party,
                                                     idents_shares=self.party_idents)
            self.logging.info(f"Secret[{l_Node[i]}], Node[{i}], Shares[{i + 2}]: {shares}")
            for xx in range(self.nums_party):
                l_NodesharesforC[xx].append(shares[xx])

        self.logging.info(
            f"len(l_NodesharesforC) = {len(l_NodesharesforC)}, len(l_NodesharesforC[0]) = {len(l_NodesharesforC[0])}")

        self.logging.info(f"l_NodesharesforC[0]: {l_NodesharesforC[0]}")

        # The state of each node will be shared among 10 clounds,
        # as shown in l_NodesharesforC. In this object, each row means five shares state of nodes in a cloud server.

        self.logging.info(f"original AA -> {l_Node}")
        self.logging.info(f"Generate AA ending...")
        self.logging.info("---------------------------------------")

        # todo upate AA in clouds.
        self.logging.info("Updating AA now")

        # each cloud will update AA for theirselves
        FileLen = len(l_Filshares[0])  # it is 14 for 'Alice Love Bob'

        for i in range(FileLen):
            # for each symbol in file stream
            for xx in range(self.nums_party):
                self.logging.debug(f"[B]-Server[{xx}, Input {l_Filshares[xx][i]}, State Machine {l_NodesharesforC[xx]}")

                prev_count = l_NodesharesforC[xx][-1]
                length_op2 = len(op2)
                for index in range(length_op2):
                    l_NodesharesforC[xx][length_op2 - index] = l_NodesharesforC[xx][length_op2 - index - 1] * \
                                                               l_Filshares[xx][i][op2_index[length_op2 - index - 1]]

                l_NodesharesforC[xx][-1] = l_NodesharesforC[xx][-1] + prev_count

                self.logging.debug(
                    f"[A]-Server[{xx}, Input {l_Filshares[xx][i]}, State Machine {l_NodesharesforC[xx]}\n")

        self.logging.info("The state machine is updated according to input")

        self.logging.info("Upate AA ending...")
        self.logging.info("--------------------------------------------")

        # todo Reconstruct AA
        self.logging.info("Reconstruct AA now")
        l_node_rec = [0 for _ in range(n_node)]
        self.logging.info(f"l_Node is reinitilized {l_node_rec}")

        self.logging.info(f"The identifier of each party server is: l_xs={self.party_idents}")
        for xx in range(n_node):
            lxs = []
            lys = []
            for y in range(xx + 3):
                lxs.append(self.party_idents[y])
                lys.append(l_NodesharesforC[y][xx])

            l_node_rec[xx] = self.context.interpolate(list(zip(lxs, lys)), overflow=False)
            self.logging.info(f"l_Node[{xx}] = {l_node_rec[xx]} is recovered using lxs={lxs}, lys={lys}")

        self.logging.info(f"Reconstruct AA -> {l_node_rec}")
        self.logging.info("Reconstruct AA ending...")
        self.logging.info("-------------------------------------")

    async def string_count(self, op, op1, op2):
        """
        Paramters:
            -op: count operation
            -op1: target string, for example: ALice Love Bob!
            -op2: Search Pattern, for example: Love
        """
        assert len(op1) >= len(op2), f"Constraint Condition: len[{op1}] >= len[{op2}] does not match"

        #  the nums of nodes in automation machine to do string_match and count algorithm.
        nums_node = len(op2) + 1

        # The number of secret shares created for each secret.
        # It's value means how many participant servers would recieve secret share data
        nums_share = self.nums_party
        idents_share = self.party_idents[:nums_share]
        # The nums of participant server needed to recover each node node state based on
        #  1. The length of input (pattern)
        #  2. THe polynoimial degree to encode shares for each bit of char
        #  For example:
        #   -   len_input (1), degree (1) -> {0:3, 1:4}
        #   -   len_input (1), degree (2) -> {0:5, 1:7}
        #   -   len_input (1), degree (3) -> {0:7, 1:10}
        # The above value indicates the at least number servers that we need, of course, we can
        # use all participants servers to do recover job
        get_nums_server = lambda x: (2 + x) * self.poly_order + 1

        max_nums_server = get_nums_server(len(op2))
        assert max_nums_server <= nums_share, \
            f"The max nums of servers [{max_nums_server}] needed to recover data is less than {nums_share}"

        func_shares = partial(self.share_engine.create_shares,
                              nums_shares=nums_share,
                              idents_shares=idents_share)

        # ********************** State autormation machine
        automation_machine = [1 if x == 0 else 0 for x in range(nums_node)]
        automation_shares_vec = np.array([func_shares(secret=x, poly_order=idx + 2 * self.poly_order)
                                          for idx, x in enumerate(automation_machine)]) \
            .reshape((len(automation_machine), nums_share))
        automation_shares = automation_shares_vec.transpose()  # 2D numpy array: nums_share * nums_node

        await self.distribute("state", automation_shares, nums_share)
        if self.context.isDebug:
            self.logging.debug(f"The orignial automation shares vector \n{automation_shares}")

        # ********************** First Operator
        op1_shares = self.create_shares(op1, self.poly_order, nums_share, idents_share)
        await self.distribute("op1", op1_shares, nums_share)

        # ********************** Second operator
        op2_index = np.array([self.embedding.alphabet_list.index(char) for char in op2])

        # 2d numpy array numpy_share * len_op2
        op2_dist = np.tile(op2_index, nums_share).reshape((nums_share, op2_index.size))
        await self.distribute("op2", op2_dist, nums_share)

        if self.context.isDebug:
            self.logging.debug(f"The orignial op2 shares vector \n{op2_dist}")
            for idx, share in enumerate(op2_dist):
                share = str(share).replace('\n', '')
                self.logging.debug(f"op1-[{op2}]-[{idx}] distribute shares: {share}")

        recover_shares = await self.execute_command(op, nums_server=nums_share, nums_share=nums_share)

        result = []
        for index in range(nums_node):
            # Need at least [index+3] nodes to recover dataset
            node_state = [(ident, reg[index]) for ident, reg in recover_shares[:get_nums_server(index)]]

            node_value = self.context.interpolate(node_state)
            self.logging.debug(f"Node[{index}] = {node_value} is recovered by using {node_state}")
            result.append(node_value)

        expected = op1.count(op2)
        op_str = "count"
        self.logging.info(f"Result[{op1} {op_str} {op2}]: expected {expected}, real {result}")

    async def match(self, op, op1, op2):
        assert len(op1) == len(op2), f"The lenght of [{op1}] and [{op2}] does not match"

        # The number of secret shares created for each secret.
        # It's value means how many participant servers would recieve secret share data
        nums_share = self.nums_party
        idents_share = self.party_idents[:nums_share]

        # nums_server = 2 * len(op1) + 1
        nums_server = nums_share
        assert nums_server <= nums_share, \
            f"Recover {op1, op2} need at least {nums_server} servers (<= {nums_share})"

        op1_shares = self.create_shares(op1, self.poly_order, nums_share, idents_share)
        await self.distribute("op1", op1_shares, nums_share)

        op2_shares = self.create_shares(op2, self.poly_order, nums_share, idents_share)
        await self.distribute("op2", op2_shares, nums_share)

        recover_shares = await self.execute_command(op, nums_server=nums_share, nums_share=nums_share)

        result = self.context.interpolate(recover_shares)

        expected = 1 if op1 == op2 else 0
        op_str = "=="
        self.logging.debug(f"Using data {recover_shares}")
        self.logging.info(
            f"Result[{op1} {op_str} {op2}]: expected {expected}, real {result}, diff {expected - result}")

    async def calc(self, op, op1=13, op2=5):
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

    async def distribute(self, label, secret_shares, nums_share):
        """
        Distribute secret shares to first [nums_share] selected participants
        Paramters
            label: a label name identifying the data
            secret_shares: a list of secret shares
            nums_share: the number of partipant servers will recieve data
        """
        for idx, uri in enumerate(self.partyServers[:nums_share]):
            share = secret_shares[idx]
            async with websockets.connect(uri) as websocket:
                message = self.event.serialization(self.event.type.data, label, share)
                # data sent to/(recieved from) servers must be bytes, str, or iterable
                await websocket.send(message)

    async def test_calc(self):
        await self.calc(self.event.type.sub, 15, 16)
        await self.calc(self.event.type.add, 2, 3)
        await self.calc(self.event.type.mul, 8000000000, 5600000000)

    async def test_match(self):
        from functools import reduce
        nums_str = 5
        for i in range(self.embedding.alphabet_size):
            xs = reduce(lambda x, y: x + y, [self.embedding.alphabet_list[i] for i in
                                             self.context.generate_random(min=0, max=self.embedding.alphabet_size, nums=nums_str)])
            ys = reduce(lambda x, y: x + y, [self.embedding.alphabet_list[i] for i in
                                             self.context.generate_random(min=0, max=self.embedding.alphabet_size, nums=nums_str)])
            await self.match(self.event.type.match, xs, ys)
            await self.match(self.event.type.match, xs, xs)
            await self.match(self.event.type.match, ys, ys)

    async def producer_handler(self):

        start = time.time()
        await self.test_match()
        await self.test_calc()
        await self.aa_count_sage_standalone()
        await self.string_count(self.event.type.string_count, 'Bob Love ALice', 'L')
        await self.match(self.event.type.match, "ABCed", "ABCed")

        end = time.time()
        self.logging.info(f"The execution time {end - start}")

    def start(self):
        asyncio.get_event_loop().run_until_complete(self.producer_handler())
