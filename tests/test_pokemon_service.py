import unittest.mock as mock
import pytest

from polars import DataFrame
from pokepy import pokemon_service
from pokepy.pokemon_service import SortDirection


@pytest.fixture
def pokemon_dataframe() -> DataFrame:
    return DataFrame({
        "name": ["squirtle", "charmander", "bulbasaur", "pikachu"],
        "primary_type": ["water", "fire", "grass", "electric"],
        "held_item": [None, "lum berry", None, "choice scarf"],
    })

@mock.patch("pokepy.pokemon_service.requests.get")
def test_get_image_returns_none_when_pokemon_not_found(mock_get):
    mock_response = mock.Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    actual_response = pokemon_service.get_image("pikachu")

    assert actual_response is None


def test_sort_datatable_sorts_ascending(pokemon_dataframe: DataFrame):
    # arrange
    sort_direction = SortDirection.ASCENDING
    column_name = "name"

    # act
    sorted_dataframe = pokemon_service.sort_dataframe(
        dataframe=pokemon_dataframe,
        column_name=column_name,
        sort_direction=sort_direction,
    )

    # assert
    first_name = sorted_dataframe["name"][0]
    last_name = sorted_dataframe["name"].last()

    assert first_name == "bulbasaur"
    assert last_name == "squirtle"


def test_sort_datatable_sorts_descending(pokemon_dataframe: DataFrame):
    # arrange
    sort_direction = SortDirection.DESCENDING
    column_name = "name"

    # act
    sorted_dataframe = pokemon_service.sort_dataframe(
        dataframe=pokemon_dataframe,
        column_name=column_name,
        sort_direction=sort_direction,
    )

    # assert
    first_name = sorted_dataframe["name"][0]
    last_name = sorted_dataframe["name"].last()

    assert first_name == "squirtle"
    assert last_name == "bulbasaur"
