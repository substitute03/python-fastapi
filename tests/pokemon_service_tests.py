import pytest
import pokemon_service
import unittest.mock as mock

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
