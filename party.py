from src.utils.context import Context
from src.party.party import PartyServer

if __name__ == "__main__":
    ctx = Context('party')
    logging = ctx.logger
    partyServer = PartyServer(ctx)
    partyServer.start()