#!/usr/bin/env python3
import gzip
import json
import os
import tempfile
import zipfile
import click
from shapely.geometry import shape


def _load_geojson(filepath):
    """Load a geojson, that can be a plain file, a zip or a gzip file"""
    if filepath.lower().endswith(".zip"):
        with tempfile.TemporaryDirectory() as tmpdir, zipfile.ZipFile(filepath) as zip_ref:
            geojson_filename = next((filename for filename in zip_ref.namelist() if filename.lower().endswith((".geojson", ".json"))), None)

            if geojson_filename is None:
                raise ValueError(f"No GeoJSON file found in the zip archive: {filepath}")

            zip_ref.extract(geojson_filename, tmpdir)
            geojson_filepath = os.path.join(tmpdir, geojson_filename)

            return _load_plain_geojson(geojson_filepath)
    elif filepath.lower().endswith(".gz"):
        return _load_gzip_geojson(filepath)
    else:
        return _load_plain_geojson(filepath)


def _load_plain_geojson(filepath):
    """Load a plain geojson file."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def _load_gzip_geojson(filepath):
    """Load a gzip compressed geojson file."""
    with gzip.open(filepath, "rb") as gz_file:
        return json.load(gz_file)


def _extract_state_geometries(states_data, state_name_field):
    """Extract state geometries from the state GeoJSON data."""
    state_geometries = {}
    for state_feature in states_data["features"]:
        if state_feature["geometry"] is None:
            continue
        try:
            state_name = state_feature["properties"][state_name_field]
        except KeyError as exc:
            raise KeyError(f"`{state_name_field}` not found in properties: {state_feature['properties'].keys()}") from exc
        state_geometries[state_name] = shape(state_feature["geometry"])
    return state_geometries


def _assign_features_to_states(input_data, state_geometries):
    """Assign input features to states based on intersection."""
    state_features = {}

    for feature in input_data["features"]:
        feature_geom = shape(feature["geometry"])

        for state_name, state_geom in state_geometries.items():
            intersection = state_geom.intersection(feature_geom)

            if not intersection.is_empty:
                state_features.setdefault(state_name, []).append(feature)

    return state_features


def _write_features_to_files(output_dir, state_features, original_filename):
    """Write features for each state to separate GeoJSON files."""

    for state_name, features in state_features.items():
        output_path = os.path.join(output_dir, f"{original_filename}_{state_name}.json")
        output_data = {"type": "FeatureCollection", "features": features}

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

        click.echo(f"Output: {output_path}. {len(features)} features saved for {state_name}")


def split_geojson_by_state(states_geojson_path, input_geojson_path, output_dir, state_name_field):
    """
    Splits a GeoJSON file into multiple files based on the state boundaries defined in another GeoJSON.

    Args:
        states_geojson_path: Path to the GeoJSON file containing state boundaries.
        input_geojson_path: Path to the GeoJSON file to be split.
        output_dir: Directory to save the split GeoJSON files.
        state_name_field: The name of the field in the state GeoJSON properties containing the state name.
    """
    original_filename = os.path.basename(input_geojson_path).rsplit(".", 1)[0]

    states_data = _load_geojson(states_geojson_path)
    input_data = _load_geojson(input_geojson_path)

    os.makedirs(output_dir, exist_ok=True)
    state_geometries = _extract_state_geometries(states_data, state_name_field)
    state_features = _assign_features_to_states(input_data, state_geometries)
    _write_features_to_files(output_dir, state_features, original_filename)


@click.command()
@click.argument("states_geojson_path", type=click.Path(exists=True))
@click.argument("input_geojson_path", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path())
@click.argument("state_name_field", type=click.STRING)
def main(states_geojson_path, input_geojson_path, output_dir, state_name_field):
    """
    Splits a GeoJSON file into multiple files based on state boundaries.
    """
    split_geojson_by_state(states_geojson_path, input_geojson_path, output_dir, state_name_field)


if __name__ == "__main__":
    main()  # pylint:disable=no-value-for-parameter
