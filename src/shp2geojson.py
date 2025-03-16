#!/usr/bin/env python3
import json
import shutil
import zipfile
from contextlib import contextmanager
from pathlib import Path
import click
import fiona
from fiona.errors import DriverError
from fiona.model import to_dict


@contextmanager
def temp_extract_dir(input_zip_file):
    """Context manager for creating and cleaning up a temporary directory."""
    temp_dir = Path("temp_shp_extract")
    temp_dir.mkdir(exist_ok=True)
    try:
        with zipfile.ZipFile(input_zip_file, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        yield temp_dir
    finally:
        try:
            shutil.rmtree(temp_dir)
        except OSError as exc:
            click.echo(
                f"Error: Could not remove temporary directory {temp_dir} due to: {exc}",
                err=True,
            )


def _shapefile_to_geojson(input_zip_file, output_geojson_path):
    """
    Convert a zipped shapefile to GeoJSON.

    INPUT_ZIP_FILE: Path to the zipped shapefile
    OUTPUT_GEOJSON_FILE: Path to the output GeoJSON file
    """

    with temp_extract_dir(input_zip_file) as temp_dir:
        # Find the .shp file in the extracted contents
        shp_file = None
        for file in temp_dir.rglob("*.shp"):
            shp_file = file
            break

        if not shp_file:
            raise FileNotFoundError("No .shp file found in the zip archive")

        if not Path(str(shp_file).replace(".shp", ".shx")).exists():
            raise FileNotFoundError("No .shx file found in the zip archive")

        if not Path(str(shp_file).replace(".shp", ".dbf")).exists():
            raise FileNotFoundError("No .dbf file found in the zip archive")

        # Read the shapefile and convert to GeoJSON
        geojson_data = {"type": "FeatureCollection", "features": []}

        with fiona.open(shp_file, "r") as source:
            for feature in source:
                plain_feature = to_dict(feature)
                geojson_data["features"].append(plain_feature)

        # Write to GeoJSON file
        with open(output_geojson_path, "w", encoding="utf-8") as geojson_file:
            json.dump(geojson_data, geojson_file, indent=2)
        click.echo(f"Conversion complete: {output_geojson_path}. {len(geojson_data['features'])} features converted.")


@click.command("shp2geojson")
@click.argument("input_zip_file", type=click.Path(exists=True))
@click.argument("output_geojson_path", type=click.Path())
def shapefile_to_geojson(input_zip_file, output_geojson_path):
    try:
        _shapefile_to_geojson(input_zip_file, output_geojson_path)
    except (zipfile.BadZipFile, DriverError) as exc:
        raise click.ClickException(f"Error processing zip file: {exc}") from exc
    except Exception as exc:
        raise click.ClickException(f"Error: {exc}") from exc


if __name__ == "__main__":
    shapefile_to_geojson()  # pylint: disable=no-value-for-parameter
