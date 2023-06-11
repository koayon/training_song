"Example of how to use the training_song module."

from trainingsong.core import ts
import asyncio

if __name__ == "__main__":
    acc, response = asyncio.run(ts(92, autoplay=True, verbose=True, chart="hot-100"))

    # print(acc)
