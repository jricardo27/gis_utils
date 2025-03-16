import json
import os
import tempfile
import pytest
from src.geojson_simplify import _geojson_simplify


def test_geojson_simplify_success():
    """Test the geojson_simplify function with a valid geojson file."""
    # Create a test geojson
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [1, 1],
                            [1, 2],
                            [1.5, 1.5],
                            [2, 2],
                            [2, 1],
                            [1, 1],
                        ]
                    ],
                },
                "properties": {},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [3, 3],
                                [3, 4],
                                [3.5, 3.5],
                                [4, 4],
                                [4, 3],
                                [3, 3],
                            ]
                        ],
                        [
                            [
                                [6, 6],
                                [6, 7],
                                [6.5, 6.5],
                                [7, 7],
                                [7, 6],
                                [6, 6],
                            ]
                        ],
                    ],
                },
                "properties": {},
            },
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".geojson") as temp_input_geojson:
        json.dump(data, temp_input_geojson)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as temp_output_geojson:
        _geojson_simplify(
            input_path=temp_input_geojson.name,
            output_geojson_path=temp_output_geojson.name,
            tolerance=1,
        )

        assert os.path.exists(temp_output_geojson.name)

        # Check if the output is valid GeoJSON
        with open(temp_output_geojson.name, encoding="utf-8") as f:
            try:
                geojson_data = json.load(f)
                # Check if the output has fewer points
                assert len(data["features"][0]["geometry"]["coordinates"][0]) == 6
                assert len(geojson_data["features"][0]["geometry"]["coordinates"][0]) == 5
                assert len(data["features"][1]["geometry"]["coordinates"][0][0]) == 6
                assert len(geojson_data["features"][1]["geometry"]["coordinates"][0][0]) == 5
                assert len(data["features"][1]["geometry"]["coordinates"][1][0]) == 6
                assert len(geojson_data["features"][1]["geometry"]["coordinates"][1][0]) == 5
            except json.JSONDecodeError:
                pytest.fail("Output file is not valid GeoJSON")

    os.unlink(temp_input_geojson.name)
    os.unlink(temp_output_geojson.name)
