from src.utils.context import Context
from src.client.user import UserClient

if __name__ == "__main__":
    ctx = Context('client')
    client = UserClient(ctx)
    client.start()
