from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel
import base64
from pokemon_image_service import get_image
from typing import Literal
import pandas as pd

app = FastAPI()

class PokemonImagesResponse(BaseModel):
    base64_images_by_name: dict[str, str]
    could_not_get_images: list[str]

class PokemonCsvRequest(BaseModel):
    csv_file: UploadFile = File(...)
    sort_by_field: str
    sort_direction: Literal["asc", "desc"]

class NewPokemonParquetResponse(BaseModel):
    parquet_file: UploadFile = File(...)

@app.get("/pokemon/image/{pokemon_name}")
async def get_pokemon_image(pokemon_name: str):
    image = get_image(pokemon_name)

    if image is None:
        raise HTTPException(status_code = 404, detail = "Pokemon not found")
    else:
        return Response(content=image, media_type="image/png")

@app.post("/pokemon/images/", response_model=PokemonImagesResponse)
async def get_pokemon_images(pokemon_names: list[str]):
    bytes_images_by_name: dict[str, bytes] = {}
    could_not_get_images: list[str] = []

    for name in pokemon_names:
        image_or_none = get_image(name)

        if image_or_none is None:
            could_not_get_images.append(name)
        else:
            bytes_images_by_name[name] = image_or_none

    if len(bytes_images_by_name) == 0:
        raise HTTPException(status_code = 404, detail = "Failed to get any images")
    else:
        # encode the images to base64 so they can be serialized to json
        base64_images_by_name: dict[str, str] = {}
        for name in bytes_images_by_name:
            base64_images_by_name[name] = base64.b64encode(bytes_images_by_name[name]).decode("ascii")

        return PokemonImagesResponse (
            base64_images_by_name = base64_images_by_name,
            could_not_get_images = could_not_get_images
        )

# Converts a CSV file of pokemon names into a parquet file with images
# The CSV input should have a column called "name" with the pokemon names
# the CSV input can have other columns that can be sorted by, but should not have a column called "image"
# The parquet output will add a column called "image" with the base64 encoded image
# The parquet file will be sorted by the specified field and direction
@app.post("/pokemon/ideas/csv-to-parquet", response_model = None)
async def get_parquet_from_csv(
    csv_file: UploadFile = File(...),
    sort_by_field: str = Form(...),
    sort_direction: Literal["asc", "desc"] = Form(...)
):
    could_not_get_images: list[str] = []

    # read the csv file into a pandas dataframe
    df = pd.read_csv(csv_file.file)

    if "name" not in df.columns:
        raise HTTPException(status_code = 400, detail = "CSV file must have a column called 'name'")

    if sort_by_field not in df.columns:
        raise HTTPException(status_code = 400, detail = "The specified sort by field is not in the CSV file")

    # get the image for each pokemon and add it to the dataframe
    names: list[str] = df["name"].tolist()
    for name in df["name"]:
        image = get_image(name)

        if image is None:
            could_not_get_images.append(name)
            df.loc[df["name"] == name, "image"] = "Not found"
        else:
            df.loc[df["name"] == name, "image"] = base64.b64encode(image).decode("ascii")

    # sort the dataframe by the specified field and direction
    df = df.sort_values(
        by = sort_by_field,
        ascending = True if sort_direction == 'asc' else False
    )

    # convert the dataframe to a parquet file
    parquet_file = df.to_parquet()

    return Response(
        content=parquet_file,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=pokemon.parquet"},
    )