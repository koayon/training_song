# Training Song

<div align="center">
    <img src="https://github.com/koayon/training_song/actions/workflows/tests.yaml/badge.svg" alt="Tests">
    <img src="https://img.shields.io/pypi/v/training-song?color=%2334D058&label=pypi%20package" alt="Package version">
   <img src="https://img.shields.io/pypi/pyversions/training-song.svg?color=%2334D058" alt="Supported Python versions">
</div>

## Description

Plays a Billboard Number 1 song corresponding to how accurate your ML model is.

For example if your model is 95.5% accurate then you will hear the number 1 song from 50% through 1995 (Vogue by Madonna 👑).

Take your metrics from [A Hard Day's Night](https://open.spotify.com/track/5J2CHimS7dWYMImCHkEFaJ?si=a0e9062fc8674757) (64%) to [Mo Money Mo Problems](https://open.spotify.com/track/4INDiWSKvqSKDEu7mh8HFz?si=81e7a21927d741c7) (97%).

## How to use

Once you've trained your model, simply wrap your metric in ts(..) as follows:

```python
from trainingsong import ts

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

accuracy = ts(accuracy_score(y_test, y_pred))

>> Congrats your model got an accuracy of 92 percent!
>> The Number 1 song 92.0% through the 1900s on the hot-100 chart was
   Black Or White by Michael Jackson.
>> The date was 1992-01-01 and the song was on the chart for 7 weeks.
```

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install trainingsong.

```bash
pip install training-song
```

## Local Development

The API docs can be found [here](https://training-song-api-koayon.vercel.app/docs)

You can install the development dependencies with:

```bash
poetry install
```

And you can run the tests using

```bash
poetry run pytest
```

Before committing, please run the following to run the tests:

```bash
tox
```

It's recommended to use uvicorn to run the server locally, which is
installed as a dependency.

Please create a Postgres database and set the DATABASE_URL as an environment
variable in the .env file. The db.py file defines the schema and gives a function
to create the table.

Additionally if you're editing the main API then you will need to create a [Spotify app](https://developer.spotify.com/)
and set include the CLIENT_ID and CLIENT_SECRET as environment variables.
In this case you will also need to setup a [Vercel](https://vercel.com/) account and deploy the API to it.
Then you can use the [Vercel CLI](https://vercel.com/docs/cli) to run the server locally.

```bash
vercel .
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT

### Acknowledgements

Thanks to [Spotify](https://developer.spotify.com/) for the API and [Billboard](https://www.billboard.com/charts/hot-100) for the data.

[![Substack](https://img.shields.io/badge/Substack-%23006f5c.svg?style=for-the-badge&logo=substack&logoColor=FF6719)](https://lookingglassworld.substack.com)
