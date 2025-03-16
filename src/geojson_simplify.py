#!/usr/bin/env python3
import gzip
import json
import os
import tempfile
import zipfile
import click
from shapely import simplify
from shapely.geometry import mapping, shape
from shapely.geometry.multipolygon import MultiPolygon


def _simplify_polygon(polygon, tolerance):
    """Simplifies a Polygon and returns the point counts."""
    points_before = len(polygon.exterior.coords)
    simplified_polygon = simplify(polygon, tolerance)
    points_after = len(simplified_polygon.exterior.coords)

    return mapping(simplified_polygon), points_before, points_after


def _simplify_multipolygon(multipolygon, tolerance):
    """Simplifies a MultiPolygon and returns the point counts."""
    simplified_polygons = []
    points_before = 0
    points_after = 0

    for polygon in multipolygon.geoms:
        points_before += len(polygon.exterior.coords)
        simplified_polygon = simplify(polygon, tolerance)
        points_after += len(simplified_polygon.exterior.coords)
        simplified_polygons.append(simplified_polygon)

    return mapping(MultiPolygon(simplified_polygons)), points_before, points_after


def _geojson_simplify(input_path, output_geojson_path, tolerance):
    """
    Simplify polygons in a GeoJSON file or a zip file containing a geojson.

    INPUT_PATH: Path to the input GeoJSON file or zip file.
    OUTPUT_GEOJSON_PATH: Path to the output GeoJSON file.
    """
    if zipfile.is_zipfile(input_path):
        with tempfile.TemporaryDirectory() as tmpdir, zipfile.ZipFile(input_path) as zip_ref:
            geojson_filename = None
            for filename in zip_ref.namelist():
                if filename.lower().endswith(".geojson") or filename.lower().endswith(".json"):
                    geojson_filename = filename
                    break

            if geojson_filename is None:
                raise ValueError(f"No GeoJSON file found in the zip archive: {input_path}")

            zip_ref.extract(geojson_filename, tmpdir)
            input_geojson_path = os.path.join(tmpdir, geojson_filename)
            _process_geojson_file(input_geojson_path, output_geojson_path, tolerance, input_path)
    elif input_path.lower().endswith(".gz"):
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".json", dir=tmpdir) as temp_decompressed_file,
        ):
            decompressed_filename = temp_decompressed_file.name

            # Decompress the .gz file and write to the temporary file
            with gzip.open(input_path, "rb") as gz_file:
                temp_decompressed_file.write(gz_file.read())  # type: ignore

            input_geojson_path = os.path.join(tmpdir, decompressed_filename)
            _process_geojson_file(input_geojson_path, output_geojson_path, tolerance, input_path)
    else:
        _process_geojson_file(input_path, output_geojson_path, tolerance, input_path)


def _process_geojson_file(input_geojson_path, output_geojson_path, tolerance, original_input_path):
    """Process the geojson file and saves the simplified version"""

    def _get_unique_output_path(base_path):
        """Appends numbers to the output path to make it unique"""
        if not os.path.exists(base_path):
            return base_path

        counter = 1
        while True:
            new_path = f"{base_path.rsplit('.', 1)[0]}_{counter}.{base_path.rsplit('.', 1)[1]}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    with open(input_geojson_path, encoding="utf-8") as f:
        geojson_data = json.load(f)

    for index, feature in enumerate(geojson_data["features"]):
        if feature["geometry"] is None:
            continue

        original_geom = shape(feature["geometry"])

        if original_geom.geom_type == "Polygon":
            feature["geometry"], points_before, points_after = _simplify_polygon(original_geom, tolerance)
        elif original_geom.geom_type == "MultiPolygon":
            feature["geometry"], points_before, points_after = _simplify_multipolygon(original_geom, tolerance)
        else:
            continue

        click.echo(f"Feature {index}: Points before {points_before}, points after {points_after}")

    if not output_geojson_path:
        if zipfile.is_zipfile(original_input_path):
            filepath, _ = original_input_path.rsplit(".", 1)
        else:
            filepath, _ = original_input_path.rsplit(".", 1)

        extension = original_input_path.rsplit(".", 1)[1] if original_input_path.lower().endswith(".geojson") else "json"
        output_geojson_path = _get_unique_output_path(f"{filepath}_simplified.{extension}")

    with open(output_geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)

    click.echo(f"Input: {original_input_path}. Output: {output_geojson_path}.")


@click.command("geojson-simplify")
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_geojson_path", type=click.Path(), required=False, default="")
@click.option(
    "--tolerance",
    default=0.001,
    type=float,
    help="Simplification tolerance (in degrees for lat/long).",
)
def geojson_simplify(input_path, output_geojson_path, tolerance):
    _geojson_simplify(input_path, output_geojson_path, tolerance)


if __name__ == "__main__":
    geojson_simplify()  # pylint: disable=no-value-for-parameter
