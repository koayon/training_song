"Example of how to use the training_song module."

# TODO: Train simple classifier as a more credible example as well.
# TODO: Should this be a notebook instead (Titanic?) or in the README?

from trainingsong.core import ts
import asyncio

if __name__ == "__main__":
    acc, response = asyncio.run(ts(92, autoplay=True, verbose=True, chart="hot-100"))

    print(acc)
