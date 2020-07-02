# https://realpython.com/async-io-python/
import time
import asyncio


def main_nonasync():
    def count_nonasync():
        print("One")
        time.sleep(1)
        print("Two")
    for _ in range(3):
        count_nonasync()


async def main_async():
    async def count_async():
        print("One")
        await asyncio.sleep(1)
        print("Two")

    await asyncio.gather(count_async(), count_async(), count_async())

if __name__ == "__main__":
    s = time.perf_counter()
    main_nonasync()
    asyncio.run(main_async())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")