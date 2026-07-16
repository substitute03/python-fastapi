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

## API endpoints

### `GET /pokemon/image/{pokemon_name}`

Returns a single Pokemon sprite as PNG.

- **200** — `image/png` body
- **404** — Pokemon not found

### `POST /pokemon/images/base64`

Request body: JSON array of names, e.g. `["pikachu", "squirtle"]`.

Response (`PokemonImagesResponse`):

- `base64_images_by_name` — map of name → base64-encoded image
- `could_not_get_images` — names that could not be resolved

- **404** — if no images could be fetched

### `POST /pokemon/images`

Request body: JSON array of names (same as above).

Returns a zip download (`pokemon.zip`) containing:

- one `.jpg` per successfully fetched Pokemon
- optional `could_not_get_images.txt` listing names that failed

- **404** — if no images could be fetched

### `POST /pokemon/ideas/csv-to-parquet`

Multipart form:

| Field | Type | Description |
| --- | --- | --- |
| `csv_file` | file | CSV that must include a `name` column and the sort column |
| `sort_by_field` | string | Column to sort by |
| `sort_direction` | `asc` or `desc` | Sort order |

Response: parquet download (`pokemon.parquet`) with an added `image` column (base64 string, or `"Not found"`).

- **400** — missing required columns

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
