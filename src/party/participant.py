import asyncio
import websockets
from utils.context import Context
import ssl


class ParticipantServer:
    def __init__(self, ctx, loop=None, cert_path: str = None, key_path: str = None):
        self.context = ctx
        self.logging = ctx.logger

        self.sever_id = ctx.party_id
        self.host, self.port = ctx.partyServers[self.sever_id]

        self.loop = loop if loop is not None else asyncio.new_event_loop()
        self.cert_path = cert_path
        self.key_path = key_path

    async def consumer(self, message, websocket):
        msg = int(message, 2)
        self.logging.info(
            f"Party Server [{self.sever_id}] recieve [{msg}] from ws://{websocket._host}:{websocket._port}")

        greeting = msg + 1

        await websocket.send(bin(greeting))
        self.logging.info(f"Message [{greeting}] is sent back to ws://{websocket._host}:{websocket._port}")

    async def consumer_handler(self, websocket, path):
        async for message in websocket:
            await self.consumer(message, websocket)

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
