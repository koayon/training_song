"Example of how to use the training_song module."

from trainingsong.core import ts

if __name__ == "__main__":
    acc, response = ts(92, autoplay=False, verbose=True, chart="hot-100")

    # print(acc)
