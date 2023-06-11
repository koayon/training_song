# Training Song

## Description

Plays a Billboard Number 1 song corresponding to how accurate your ML model is.

## How to use

Once you've trained your model call training_song on your final accuracy result as follows:

```python
from trainingsong.core import ts
import asyncio

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
acc, result = asyncio.run(ts(accuracy))

>> Congrats your model got an accuracy of 92 percent!
>> The Number 1 song 92.0% through the 1900s on the hot-100 chart was Black Or White by Michael Jackson.
>>  The date was 1992-01-01 and the song was on the chart for 7 weeks.
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
