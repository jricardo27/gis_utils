import json
import os
import tempfile
import zipfile
import fiona
import pytest
from click.testing import CliRunner
from fiona.crs import CRS  # pylint:disable=no-name-in-module
from ..shp2geojson import _shapefile_to_geojson, shapefile_to_geojson


@pytest.fixture(name="sample_shapefile")
def fixture_sample_shapefile(tmp_path):
    """Create a valid sample zipped shapefile for testing."""
    # Define the schema for a point shapefile
    schema = {"geometry": "Point", "properties": {"id": "int"}}
    crs = CRS.from_epsg(4326)  # WGS 84

    # Create a valid shapefile with fiona
    with fiona.open(
        tmp_path / "sample.shp",
        "w",
        driver="ESRI Shapefile",
        crs=crs.to_string(),
        schema=schema,
    ) as shapefile:
        shapefile.write({
            "geometry": {"type": "Point", "coordinates": (10, 10)},
            "properties": {"id": 1},
        })
        shapefile.write({
            "geometry": {"type": "Point", "coordinates": (20, 20)},
            "properties": {"id": 2},
        })

    # Create the zip
    with zipfile.ZipFile(tmp_path / "sample.zip", "w") as zipf:
        zipf.write(tmp_path / "sample.shp", arcname="sample.shp")
        zipf.write(tmp_path / "sample.dbf", arcname="sample.dbf")
        zipf.write(tmp_path / "sample.shx", arcname="sample.shx")

    return tmp_path / "sample.zip"


def test_zip_shapefile_to_geojson_success(sample_shapefile):
    """Test the zip_shapefile_to_geojson function with a valid zipped shapefile."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as temp_geojson:
        _shapefile_to_geojson(input_zip_file=str(sample_shapefile), output_geojson_path=temp_geojson.name)

        assert os.path.exists(temp_geojson.name)

        # Check if the output is valid GeoJSON
        with open(temp_geojson.name, encoding="utf-8") as f:
            try:
                geojson_data = json.load(f)
                assert len(geojson_data["features"]) == 2
            except json.JSONDecodeError:
                pytest.fail("Output file is not valid GeoJSON")
    os.unlink(temp_geojson.name)


def test_zip_shapefile_to_geojson_file_not_found():
    """Test the zip_shapefile_to_geojson function when the input zip file is not found."""
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as temp_geojson:
        result = runner.invoke(
            shapefile_to_geojson,
            ["not_a_file.zip", temp_geojson.name],
        )

        assert result.exit_code == 2
    os.unlink(temp_geojson.name)
