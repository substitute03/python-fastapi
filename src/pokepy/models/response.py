from pydantic import BaseModel


class PokemonImagesResponse(BaseModel):
    base64_images_by_name: dict[str, str]
    could_not_get_images: list[str]
