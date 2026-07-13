# PokePy

FastAPI service for fetching Pokemon images from [PokeAPI](https://pokeapi.co/).

## Setup

```powershell
poetry install
```

## Run the API

```powershell
poetry run uvicorn pokepy.pokemon_image_api:app --reload
```

Or:

```powershell
poetry run fastapi dev src/pokepy/pokemon_image_api.py
```

Interactive docs: http://127.0.0.1:8000/docs

## Run the console app

```powershell
poetry run pokepy-console
```

Or:

```powershell
poetry run python -m pokepy.console_app
```

## Run tests

```powershell
poetry run pytest
```
