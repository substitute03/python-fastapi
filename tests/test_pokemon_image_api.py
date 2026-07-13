import pandas as pd

from pokepy import pokemon_service


def test_missing_column_names_returned_when_columns_missing():
    df = pd.DataFrame({
        "name": ["Bulbasaur", "Charmander", "Squirtle"],
        "type": ["Grass", "Fire", "Water"],
        "HP": [45, 39, 44],
        "Atk": [49, 52, 48],
        "Def": [49, 43, 65],
        "SpAtk": [65, 60, 64],
        "SpDef": [65, 50, 68],
    })

    columns_to_check = [
        "name", "type", "HP", "Atk",
        "SpAtk", "SpDef", "Spe",
    ]

    result = pokemon_service.check_for_columns(df, columns_to_check)

    assert len(result) > 0
    assert result.__contains__("Spe")


def test_http_exception_not_thrown_expected_columns_are_present():
    df = pd.DataFrame({
        "name": ["Bulbasaur", "Charmander", "Squirtle"],
        "type": ["Grass", "Fire", "Water"],
        "HP": [45, 39, 44],
        "Atk": [49, 52, 48],
        "Def": [49, 43, 65],
        "SpAtk": [65, 60, 64],
        "SpDef": [65, 50, 68],
        "Spe": [25, 43, 35],
    })

    columns_to_check = [
        "name", "type", "HP", "Atk",
        "SpAtk", "SpDef", "Spe",
    ]

    result = pokemon_service.check_for_columns(df, columns_to_check)

    assert len(result) == 0
