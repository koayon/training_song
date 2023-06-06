"Example of how to use the training_song module."

# TODO: Train simple classifier as a more credible example as well.
# TODO: Should this be a notebook instead (Titanic?) or in the README?

from training_song import ts

if __name__ == "__main__":
    acc, response = ts(84, autoplay=True, verbose=True, chart="hot-100")

    print(acc)
