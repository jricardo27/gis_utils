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

#### Parameters

-   `INPUT_ZIP_FILE`: The path to the zipped shapefile. The shapefile should be at the root of the zip file and the zip must include the `.shp`, `.shx`, and `.dbf` files.
-   `OUTPUT_GEOJSON_PATH`: The path where the output GeoJSON file should be created.

#### Example

    ```sh
    shp2geojson input.zip output.geojson
    ```

This command will read the shapefile inside `input.zip` and create an `output.geojson` file with the converted GeoJSON data.


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
