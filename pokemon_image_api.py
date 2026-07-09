from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from pydantic import BaseModel
import base64
from pokemon_image_service import get_image

app = FastAPI()
class PokemonImagesResponse(BaseModel):
    base64_images_by_name: dict[str, str]
    could_not_get_images: list[str]

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

@app.post("/pokemon/images/from-names-csv", response_model = None)
async def get_parquet_from_csv(csv_file: UploadFile = File(...)):
    csv_file_content = await csv_file.read()

    # return the csv again for now
    return Response(content=csv_file_content, media_type="text/csv")
    