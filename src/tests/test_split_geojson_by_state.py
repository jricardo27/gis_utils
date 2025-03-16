import gzip
import json
import os
import tempfile
import zipfile
from copy import deepcopy
import pytest
from ..split_by_states import split_geojson_by_state

STATES_DATA = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"STATE_NAME": "California"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-124.21216360595776, 41.991688364789326],
                        [-123.75211616376686, 33.00355182532641],
                        [-114.75422917077651, 32.74353381693339],
                        [-114.56502785695653, 34.98130460609541],
                        [-119.7592521293625, 38.76821066788523],
                        [-119.77117362239831, 41.98306338884649],
                        [-124.209929313661, 41.99461151876329],
                    ]
                ],
            },
        },
        {
            "type": "Feature",
            "properties": {"STATE_NAME": "Nevada"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-120.00631469935398, 41.98041714014769],
                        [-119.97713743300429, 38.934313451462174],
                        [-114.08351651556231, 34.526595541725925],
                        [-114.04380719530928, 41.98841730532064],
                        [-120.00631469935398, 41.98041714014769],
                    ]
                ],
            },
        },
    ],
}

INPUT_DATA = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"id": "1", "name": "California"},
            "geometry": {"type": "Point", "coordinates": [-122, 38]},
        },
        {
            "type": "Feature",
            "properties": {"id": "2", "name": "Las Vegas"},
            "geometry": {"type": "Point", "coordinates": [-115, 36]},
        },
        {"type": "Feature", "properties": {"id": "3", "name": "Reno"}, "geometry": {"coordinates": [-119.80151826650294, 39.59011853993252], "type": "Point"}},
    ],
}


def _create_geojson_file(data, suffix=".geojson"):
    """Helper function to create a temporary GeoJSON file."""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=suffix) as temp_file:
        json.dump(data, temp_file)

    return temp_file.name


def _create_zip_file(data, filename="data.geojson"):
    """Helper function to create a temporary zip file with a GeoJSON."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".geojson") as temp_geojson_file:
        json.dump(data, temp_geojson_file)
        geojson_filepath = temp_geojson_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip, zipfile.ZipFile(temp_zip, "w") as zipf:
        zipf.write(geojson_filepath, filename)

    os.unlink(geojson_filepath)

    return temp_zip.name


def _create_gz_file(data):
    """Helper function to create a temporary gzip file with a GeoJSON."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_geojson_file:
        json.dump(data, temp_geojson_file)
        geojson_filepath = temp_geojson_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".gz") as temp_gz, gzip.open(temp_gz, "wt") as gz_file, open(geojson_filepath, encoding="utf-8") as f:
        gz_file.write(f.read())

    os.unlink(geojson_filepath)

    return temp_gz.name


def test_split_geojson_by_state_success():
    """Test a successful split using plain geojson files."""
    # Create temporary files
    states_file = _create_geojson_file(STATES_DATA)
    input_file = _create_geojson_file(INPUT_DATA)
    input_filename = os.path.basename(input_file).rsplit(".", 1)[0]

    # Create a temporary output directory
    with tempfile.TemporaryDirectory() as temp_output_dir:
        # Call the function
        split_geojson_by_state(states_file, input_file, temp_output_dir, "STATE_NAME")
        _assert_output(temp_output_dir, input_filename)

    # Clean up temporary files
    os.unlink(states_file)
    os.unlink(input_file)


def test_split_geojson_by_state_success_zip():
    """Test a successful split using zip files."""
    # Create temporary files
    states_file = _create_zip_file(STATES_DATA, "states.json")
    input_file = _create_zip_file(INPUT_DATA, "input.geojson")
    input_filename = os.path.basename(input_file).rsplit(".", 1)[0]

    # Create a temporary output directory
    with tempfile.TemporaryDirectory() as temp_output_dir:
        # Call the function
        split_geojson_by_state(states_file, input_file, temp_output_dir, "STATE_NAME")
        _assert_output(temp_output_dir, input_filename)

    # Clean up temporary files
    os.unlink(states_file)
    os.unlink(input_file)


def test_split_geojson_by_state_success_gz():
    """Test a successful split using gz files."""
    # Create temporary files
    states_file = _create_gz_file(STATES_DATA)
    input_file = _create_gz_file(INPUT_DATA)
    input_filename = os.path.basename(input_file).rsplit(".", 1)[0]

    # Create a temporary output directory
    with tempfile.TemporaryDirectory() as temp_output_dir:
        # Call the function
        split_geojson_by_state(states_file, input_file, temp_output_dir, "STATE_NAME")
        _assert_output(temp_output_dir, input_filename)

    # Clean up temporary files
    os.unlink(states_file)
    os.unlink(input_file)


def test_split_geojson_by_state_state_name_not_found():
    """Test if an error is raised when the state name is not found."""
    state_data = deepcopy(STATES_DATA)
    for feature in state_data["features"]:
        feature["properties"]["STATE"] = feature["properties"]["STATE_NAME"]
        del feature["properties"]["STATE_NAME"]

    # Create temporary files
    states_file = _create_geojson_file(state_data)
    input_file = _create_geojson_file(INPUT_DATA)

    # Create a temporary output directory
    with tempfile.TemporaryDirectory() as temp_output_dir:
        # Call the function and expect an exception
        with pytest.raises(KeyError) as exc:
            split_geojson_by_state(states_file, input_file, temp_output_dir, "STATE_NAME")
        assert "`STATE_NAME` not found in properties" in str(exc.value)

    # Clean up temporary files
    os.unlink(states_file)
    os.unlink(input_file)


def _assert_output(temp_output_dir, input_filename):
    california_output_filename = f"{input_filename}_California.json"
    nevada_output_filename = f"{input_filename}_Nevada.json"

    # Check if the output files exist
    assert os.path.exists(os.path.join(temp_output_dir, california_output_filename))
    assert os.path.exists(os.path.join(temp_output_dir, nevada_output_filename))

    # Check if the content is correct
    with open(os.path.join(temp_output_dir, california_output_filename), encoding="utf-8") as f:
        california_data = json.load(f)
        assert len(california_data["features"]) == 2
        assert california_data["features"][0]["properties"]["id"] == "1"
        assert california_data["features"][1]["properties"]["id"] == "3"

    with open(os.path.join(temp_output_dir, nevada_output_filename), encoding="utf-8") as f:
        nevada_data = json.load(f)
        assert len(nevada_data["features"]) == 2
        assert nevada_data["features"][0]["properties"]["id"] == "2"
        assert nevada_data["features"][1]["properties"]["id"] == "3"
