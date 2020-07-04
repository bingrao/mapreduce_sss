from src.utils.context import Context
from src.party.party import PartyServer
from multiprocessing import Process


def start_process(ctx, party_id):  # pragma: no cover
    """
    helper function for spinning up a websocket participant
    """

    def target():
        server = PartyServer(ctx=ctx, party_id=party_id)
        server.start()

    p = Process(target=target)
    p.start()
    return p


if __name__ == "__main__":
    ctx = Context('party')
    logging = ctx.logger
    nums_server = ctx.nums_server
    logging.info(f"Start {nums_server} (<= {ctx.max_nums_server}) Websocket Servers. Press CTRL-C to stop.")
    for i in range(nums_server):
        start_process(ctx, i)

