import base64
import zipfile
import polars as pl

from functools import lru_cache
from io import BytesIO
from fastapi import Depends, FastAPI, File, Form, HTTPException, Response, UploadFile
from pokepy.models.response import PokemonImagesResponse
from pokepy.pokemon_service import SortDirection, PokemonService
from pokepy.pokemon_repository import PokemonRepository

app = FastAPI()

# Dependency injection
# lru_cache is a Python decorator that caches the result of the function.
# If it is called again with the same arguments, it will return the cached result instead of calling the function again.
@lru_cache
def get_pokemon_repository() -> PokemonRepository:
    return PokemonRepository()

def get_pokemon_service(pokemon_repository: PokemonRepository = Depends(get_pokemon_repository)) -> PokemonService:
    return PokemonService(pokemon_repository)

@app.get("/pokemon/image/{pokemon_name}")
async def get_pokemon_image(pokemon_name: str, pokemon_service: PokemonService = Depends(get_pokemon_service)):
    image = pokemon_service.get_image(pokemon_name)

    if image is None:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    else:
        return Response(content=image, media_type="image/png")


@app.post("/pokemon/images/base64", response_model=PokemonImagesResponse)
async def get_pokemon_images_base64(pokemon_names: list[str], pokemon_service: PokemonService = Depends(get_pokemon_service)):
    bytes_images_by_name: dict[str, bytes] = {}
    could_not_get_images: list[str] = []

    # remove duplicates (a set cannot have duplicates)
    pokemon_names = list(set(pokemon_names))

    for name in pokemon_names:
        image_or_none = pokemon_service.get_image(name)

        if image_or_none is None:
            could_not_get_images.append(name)
        else:
            bytes_images_by_name[name] = image_or_none

    if len(bytes_images_by_name) == 0:
        raise HTTPException(status_code=404, detail="Failed to get any images")
    else:
        base64_images_by_name: dict[str, str] = {}
        for name in bytes_images_by_name:
            base64_images_by_name[name] = base64.b64encode(bytes_images_by_name[name]).decode("ascii")

        return PokemonImagesResponse(
            base64_images_by_name=base64_images_by_name,
            could_not_get_images=could_not_get_images,
        )

@app.post("/pokemon/images")
async def get_pokemon_images(pokemon_names: list[str], pokemon_service: PokemonService = Depends(get_pokemon_service)):
    bytes_images_by_name: dict[str, bytes] = {}
    could_not_get_images: list[str] = []

    # remove duplicates (a set cannot have duplicates)
    pokemon_names = list(set(pokemon_names))

    for name in pokemon_names:
        image_or_none = pokemon_service.get_image(name)

        if image_or_none is None:
            could_not_get_images.append(name)
        else:
            bytes_images_by_name[name] = image_or_none

    if len(bytes_images_by_name) == 0:
        raise HTTPException(status_code=404, detail="Failed to get any images")

    # create a zip folder of jpgs
    zip_folder: BytesIO = BytesIO()
    with zipfile.ZipFile(zip_folder, "w") as zip_file:
        for name in bytes_images_by_name:
            # add as jpg files
            zip_file.writestr(name + ".jpg", bytes_images_by_name[name])

        # add a txt file to this zip folder with list of pokemon names
        # that could not be found
        if len(could_not_get_images) > 0:
            zip_file.writestr("could_not_get_images.txt", "\n".join(could_not_get_images))

    zip_folder_as_bytes: bytes = zip_folder.getvalue()

    return Response(
        content=zip_folder_as_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=pokemon.zip"},
    )

@app.post("/pokemon/csv-to-parquet", response_model=None)
async def get_parquet_from_csv(
    csv_file: UploadFile = File(...),
    sort_by_field: str = Form(default=None),
    sort_direction: SortDirection = Form(default=None),
    add_images: bool = Form(default=False),
    pokemon_service: PokemonService = Depends(get_pokemon_service),
):
    could_not_get_images: list[str] = []

    # df: DataFrame = pd.read_csv(csv_file.file)
    df = pl.read_csv(csv_file.file)

    column_names: list[str] = ["name"]
    if sort_by_field is not None:
        column_names.append(sort_by_field)

    missing_columns = pokemon_service.check_for_columns(df, column_names)

    if len(missing_columns) > 0:
        error: str = ""

        for name in missing_columns:
            error += f"\n{name}, "

        error = error.removesuffix(" ")

        raise HTTPException(status_code=400, detail=error)

    if add_images:
        # build a list strings ("Not found" or the base64 string) for each pokemon
        images: list[str] = []
        for name in df["name"]:
            image = pokemon_service.get_image(name)

            if image is None:
                could_not_get_images.append(name)
                images.append("Not found")
            else:
                images.append(base64.b64encode(image).decode("ascii"))

        # set the image column (aka a series) to the dataframe
        df = df.with_columns(
            pl.Series("image", images)
        )

    if sort_by_field is not None and sort_direction is not None:
        df = pokemon_service.sort_dataframe(
            dataframe=df,
            column_name=sort_by_field,
            sort_direction=sort_direction,
        )

    # create an in memory parquet file
    parquet_file: BytesIO = BytesIO()
    df.write_parquet(file=parquet_file)

    base_name = (csv_file.filename or "pokemon").removesuffix(".csv")
    parquet_file.name = f"{base_name}.parquet"

    parquet_file_as_bytes: bytes = parquet_file.getvalue()

    return Response(
        content=parquet_file_as_bytes,
        media_type="application/octet-stream",
        headers={f"Content-Disposition": f"attachment; filename={parquet_file.name}"},
    )