import requests

def get_image(pokemon_name) -> bytes | None:
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"

    try:
        response = requests.get(url)
        jsonResponse = response.json()

        if "sprites" not in jsonResponse or "front_default" not in jsonResponse["sprites"]:
            print(f"No image found for {pokemon_name}")
            return None

        image_url = jsonResponse["sprites"]["front_default"]
        image = requests.get(image_url)
        image.raise_for_status()
                
        return image.content
    except requests.exceptions.RequestException as ex:
        return None

def save_image(image, saveLocation):
    # save image to saveLocation
    with open(saveLocation, "wb") as file:
        file.write(image)