import pokemon_service
import unittest.mock as mock
import pandas as pd
import pytest
from pokemon_service import SortDirection

@pytest.fixture
def pokemon_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "name": ["squirtle", "charmander", "bulbasaur", "pikachu"],
        "primary_type": ["water", "fire", "grass", "electric"],
        "held_item": [None, "lum berry", None, "choice scarf"],
    })

# test that uses mocking
@mock.patch("pokemon_service.requests.get")
def test_get_image_returns_none_when_pokemon_not_found(mock_get):
    # arrange
    mock_response = mock.Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
 
    # act
    actual_response = pokemon_service.get_image("pikachu")

    # assert
    assert actual_response is None

def test_sort_datatable_sorts_ascending(pokemon_dataframe: pd.DataFrame):
    # arrange
    # act
    sorted_dataframe = pokemon_service.sort_dataframe(
        dataframe = pokemon_dataframe,
        column_name = "name",
        sort_direction = SortDirection.ASCENDING)

    # assert
    last_row_index = len(sorted_dataframe["name"]) - 1
    first_name = sorted_dataframe["name"].iloc[0]
    last_name = sorted_dataframe["name"].iloc[last_row_index]
    assert first_name == "bulbasaur"
    assert last_name == "squirtle"

def test_sort_datatable_sorts_descending(pokemon_dataframe: pd.DataFrame):
    # arrange
    # act
    sorted_dataframe = pokemon_service.sort_dataframe(
        dataframe = pokemon_dataframe,
        column_name = "name",
        sort_direction = SortDirection.DESCENDING)

    # assert
    last_row_index = len(sorted_dataframe["name"]) - 1
    first_name = sorted_dataframe["name"].iloc[0]
    last_name = sorted_dataframe["name"].iloc[last_row_index]
    assert first_name == "squirtle"
    assert last_name == "bulbasaur"