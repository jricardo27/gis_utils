#!/usr/bin/env python3
import json
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


def _geojson_simplify(input_geojson_path, output_geojson_path, tolerance):
    """
    Simplify polygons in a GeoJSON file.

    INPUT_GEOJSON_PATH: Path to the input GeoJSON file.
    OUTPUT_GEOJSON_PATH: Path to the output GeoJSON file.
    """
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
        filepath, extension = input_geojson_path.rsplit(".", 1)
        output_geojson_path = f"{filepath}_simplified.{extension}"

    with open(output_geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)

    click.echo(f"Input: {input_geojson_path}. Output: {output_geojson_path}.")


@click.command("geojson-simplify")
@click.argument("input_geojson_path", type=click.Path(exists=True))
@click.argument("output_geojson_path", type=click.Path(), required=False, default="")
@click.option(
    "--tolerance",
    default=0.001,
    type=float,
    help="Simplification tolerance (in degrees for lat/long).",
)
def geojson_simplify(input_geojson_path, output_geojson_path, tolerance):
    _geojson_simplify(input_geojson_path, output_geojson_path, tolerance)


if __name__ == "__main__":
    geojson_simplify()  # pylint: disable=no-value-for-parameter
