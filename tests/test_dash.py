from unittest.mock import Mock, patch

import PyHub.dash as dash


def test_fetch_weather_parses_response_fields():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 72.5,
            "apparent_temperature": 70.0,
            "relative_humidity_2m": 44,
            "wind_speed_10m": 12.5,
            "weather_code": 2,
        }
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        weather = dash.fetch_weather()

    assert weather == {
        "temp": 72.5,
        "feels_like": 70.0,
        "humidity": 44,
        "wind": 12.5,
        "description": "Partly cloudy",
    }
    mock_get.assert_called_once()
    assert mock_get.call_args.kwargs["params"]["latitude"] == dash.LATITUDE
    assert mock_get.call_args.kwargs["params"]["longitude"] == dash.LONGITUDE
