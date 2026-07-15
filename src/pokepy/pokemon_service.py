import requests

from enum import Enum
from fastapi import HTTPException
from polars import DataFrame
class SortDirection(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"

def get_image(pokemon_name: str) -> bytes | None:
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"

    try:
        response = requests.get(url)

        if response.status_code == 404:
            return None

        json_response = response.json()

        if "sprites" not in json_response or "front_default" not in json_response["sprites"]:
            print(f"No image found for {pokemon_name}")
            return None

        # use the image URL from the response to get the image
        image_url = json_response["sprites"]["front_default"]
        image = requests.get(image_url)
        image.raise_for_status()

        return image.content
    except HTTPException:
        return None


def save_image(image: bytes, saveLocation: str):
    with open(saveLocation, "wb") as file:
        file.write(image)


def sort_dataframe(dataframe: DataFrame, column_name: str, sort_direction: SortDirection) -> DataFrame:
    sort_desc = (
        True if sort_direction == SortDirection.DESCENDING
        else False
    )

    sorted_dataframe = (dataframe
        .sort(by=column_name, descending=sort_desc))

    return sorted_dataframe


def check_for_columns(dataframe: DataFrame, column_names: list[str]) -> list[str]:
    missing_columns: list[str] = []

    for name in column_names:
        if name not in dataframe.columns:
            missing_columns.append(name)

    return missing_columns
