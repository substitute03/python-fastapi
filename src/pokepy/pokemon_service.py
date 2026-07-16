import requests

from enum import Enum
from polars import DataFrame

from pokepy.pokemon_repository import PokemonRepository
class SortDirection(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"

class PokemonService:
    def __init__(self, pokemon_repository: PokemonRepository):
        self.pokemon_repository = pokemon_repository

    def get_image(self, pokemon_name: str) -> bytes | None:
        pokemon = self.pokemon_repository.get_pokemon(pokemon_name)

        if pokemon is not None:
            return pokemon.image_bytes

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

            # save to the DB so we don't have to make the API call again
            self.pokemon_repository.create_pokemon(pokemon_name, image.content)
            
            return image.content
        except requests.RequestException as e:
            print(f"HTTPError getting image for {pokemon_name}: {e}")
            return None


    def save_image(self, image: bytes, saveLocation: str):
        with open(saveLocation, "wb") as file:
            file.write(image)

    def save_image_to_dynamodb(self, image: bytes, name: str):
        self.pokemon_repository.create_pokemon(name, image)

    def sort_dataframe(self, dataframe: DataFrame, column_name: str, sort_direction: SortDirection) -> DataFrame:
        sort_desc = (
            True if sort_direction == SortDirection.DESCENDING
            else False
        )

        sorted_dataframe = (dataframe
            .sort(by=column_name, descending=sort_desc))

        return sorted_dataframe


    def check_for_columns(self, dataframe: DataFrame, column_names: list[str]) -> list[str]:
        missing_columns: list[str] = []

        for name in column_names:
            if name not in dataframe.columns:
                missing_columns.append(name)

        return missing_columns
