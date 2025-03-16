import json
import click
import pyproj
from shapely import simplify
from shapely.geometry import mapping, shape
from shapely.ops import transform


def transform_coordinates(geom, source_crs, target_crs):
    """
    Transforms coordinates of a Shapely geometry.

    Args:
        geom (shapely.geometry): Shapely geometry object.
        source_crs (str): Source coordinate reference system.
        target_crs (str): Target coordinate reference system.

    Returns:
        shapely.geometry: Transformed Shapely geometry object.
    """
    project = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True).transform
    transformed_geom = transform(project, geom)
    return transformed_geom


def _geojson_simplify(input_geojson_path, output_geojson_path, tolerance):
    """
    Simplify polygons in a GeoJSON file.

    INPUT_GEOJSON_PATH: Path to the input GeoJSON file.
    OUTPUT_GEOJSON_PATH: Path to the output GeoJSON file.
    """
    with open(input_geojson_path, encoding="utf-8") as f:
        geojson_data = json.load(f)

    for feature in geojson_data["features"]:
        original_geom = shape(feature["geometry"])
        if original_geom.geom_type == "Polygon":
            simplified_geom = simplify(original_geom, tolerance)

        elif original_geom.geom_type == "MultiPolygon":
            simplified_geom = []
            for polygon in original_geom.geoms:  # type: ignore
                simplified_polygon = simplify(polygon, tolerance)
                simplified_geom.append(simplified_polygon)
            simplified_geom = type(original_geom)(simplified_geom)  # type: ignore
        else:
            continue

        # Transform to GeoJson
        feature["geometry"] = mapping(simplified_geom)

    if not output_geojson_path:
        filepath, extension = input_geojson_path.rsplit(".", 1)
        output_geojson_path = f"{filepath}_simplified.{extension}"

    with open(output_geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f)


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
