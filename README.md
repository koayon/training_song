# Training Song

## Description

Plays a Billboard Number 1 song corresponding to how accurate your ML model is.

## How to use

Once you've trained your model call training_song on your final accuracy result as follows:

```python
from trainingsong import ts

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = ts(accuracy_score(y_test, y_pred))

>> #TODO: Insert output here
```

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install trainingsong.

```bash
pip install training-song
```

## Local Development

The API docs can be found [here](https://training-song-api-koayon.vercel.app/docs)

It's recommended to use uvicorn to run the server locally.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT

Thanks to [Spotify](https://developer.spotify.com/) for the API and [Billboard](https://www.billboard.com/charts/hot-100) for the data.
