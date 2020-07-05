from src.utils.context import Context
from src.client.user import UserClient
# watch -n 1 lsof -i -P -n
# https://www.2daygeek.com/how-to-check-whether-a-port-is-open-on-the-remote-linux-system-server/
if __name__ == "__main__":
    ctx = Context('client')
    client = UserClient(ctx)
    client.start()
