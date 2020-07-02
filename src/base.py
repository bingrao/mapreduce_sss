import websockets
import asyncio
import ssl


class BaseWorker:
    def __init__(self,
                 ctx,
                 worker_id: int,
                 host: str,
                 port: int,
                 loop=None,
                 cert_path: str = None,
                 key_path: str = None,
                 data=None):
        self.context = ctx
        self.logging = ctx.logger
        self.worker_id = worker_id
        self.host = host
        self.port = port
        self.loop = loop if loop is not None else asyncio.new_event_loop()
        self.cert_path = cert_path
        self.key_path = key_path
        self.data = data
        self.buffer_in = asyncio.Queue()
        self.buffer_out = asyncio.Queue()

    def recv_msg(self, message):
        pass

    def send_msg(self, message):
        pass

    async def consumer_handler(self, websocket: websockets.WebSocketCommonProtocol):
        pass

    async def _producer_handler(self, websocket: websockets.WebSocketCommonProtocol):
        pass

    async def _handler(self, websocket: websockets.WebSocketCommonProtocol, *args):
        pass

    def start(self):
        if self.cert_path is not None and self.key_path is not None:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.cert_path, self.key_path)
        else:
            ssl_context = None

        start_server = websockets.serve(self._handler, self.host, self.port, ssl=ssl_context)

        asyncio.get_event_loop().run_until_complete(start_server)
        self.logging.info("Serving. Press CTRL-C to stop.")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            self.logging.info("Websocket server stopped.")
