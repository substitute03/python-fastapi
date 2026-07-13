from pathlib import Path

from pokepy.pokemon_service import get_image, save_image

RED = "\033[31m"
GREEN = "\033[32m"
WHITE = "\033[0m"


def main():
    name = input(
        "Pokemon images and names sourced from https://pokeapi.co/api/v2/pokemon. "
        "Check here for specific names. Tip: for Megas, use this form: scizor-mega\n"
        "Enter a pokemon name. Use CSV syntax for multiple names: "
    )
    names = name.split(",")

    saveLocation = input("(Optional) Enter the save location (default is downloads folder): ")

    if saveLocation == "":
        saveLocation = Path.home() / "Downloads"
        print(f"No save location provided, using default location: {saveLocation}")

    for name in names:
        image = get_image(name.strip())

        if image is None:
            print(f"{RED}Failed to get image for {name}{WHITE}")
            continue

        filepath = Path(saveLocation) / f"{name.strip().lower()}.png"
        save_image(image, str(filepath))

    print(f"{GREEN}Image/s saved to {saveLocation}{WHITE}")


if __name__ == "__main__":
    main()
