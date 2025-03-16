# gis-utils

A collection of GIS utilities for working with geospatial data, primarily focused on shapefiles and GeoJSON.

## Description

This repository contains a set of command-line tools and utilities designed to simplify common tasks related to Geographic Information Systems (GIS).

## Installation

This project uses `uv` for package management.

1.  **Install `uv`**:

    If you don't have `uv` installed:

    ```sh
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
2. **Create the virtual environment:**

    ```sh
    uv venv
    ```

3. **Activate the environment:**

    ```sh
    source .venv/bin/activate
    ```

4. **Install the dependencies**:

    ```sh
    uv sync
    ```
   
## Usage

### `shp2geojson`

This command-line tool converts a zipped shapefile to GeoJSON format. The tool extracts the shapefile components from the zip archive and converts the data to GeoJSON.

#### Usage

```sh
  shp2geojson input.zip output.geojson
```

-   `<input_zip_file>`: The path to the zipped shapefile. The shapefile should be at the root of the zip file and the zip must include the `.shp`, `.shx`, and `.dbf` files.
-   `<output_geojson_path>`: The path where the output GeoJSON file should be created.


### `geojson_simplify`

Simplifies the geometry of Polygon and MultiPolygon features in a GeoJSON file using the Douglas-Peucker algorithm.

#### Usage

```sh
  geojson_simplify <input_geojson_path> <output_geojson_path> --tolerance <tolerance>
```

-   `<input_geojson_path>`: Path to the input GeoJSON or zip file.
-   `<output_geojson_path>`: Path to the output GeoJSON file. (optional). If not provided, the file will have the same name but with `_simplified` in the middle.
-   `--tolerance`: Simplification tolerance (in degrees for lat/long). Defaults to 0.001.


### `split_by_state`

Splits a GeoJSON file into multiple files based on state boundaries.

#### Usage

```sh
split_by_states <states_geojson_path> <input_geojson_path> <output_dir> <state_name_field>
```

-   `<states_geojson_path>`: Path to the GeoJSON file containing state boundaries. Can be a plain, zip or gz file.
-   `<input_geojson_path>`: Path to the GeoJSON file to be split. Can be a plain, zip or gz file.
-   `<output_dir>`: Directory to save the split GeoJSON files.
-   `<state_name_field>`: The name of the field in the state GeoJSON properties containing the state name.

The output files will be named as:

    `<original_filename>_<state_name>.json`

## Development

### Pre-commit Hooks

This project uses pre-commit to enforce code quality standards. The following
linters and formatters are configured:

  - **Ruff:** For linting and formatting Python code.
  - **Isort:** For sorting imports.
  - **Pylint:** For additional static code analysis.
  - **Pyright:** For type checking.

#### Setup

Install the pre-commit hooks:
    
    ``` sh
    pre-commit install
    ```

#### Running the Hooks Manually

To run all the hooks on all files:

    ``` sh
    pre-commit run --all-files
    ```

## License

MIT
