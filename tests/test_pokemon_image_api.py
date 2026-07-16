from unittest import mock
from polars import DataFrame
import pytest
from pokepy.pokemon_service import PokemonService
from pokepy.pokemon_repository import PokemonRepository


@pytest.fixture
def pokemon_repository() -> mock.Mock:
    return mock.Mock(spec=PokemonRepository)

@pytest.fixture
def pokemon_service(pokemon_repository: mock.Mock) -> PokemonService:
    return PokemonService(pokemon_repository)

def test_missing_column_names_returned_when_columns_missing(pokemon_service: PokemonService):
    df = DataFrame({
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


def test_http_exception_not_thrown_expected_columns_are_present(pokemon_service: PokemonService):
    df = DataFrame({
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
