"""
Database utility functions for DuckDB and other DBs.
"""
import duckdb

def get_duckdb_connection(database: str) -> duckdb.DuckDBPyConnection:
    """Create and configure a DuckDB connection."""
    con = duckdb.connect(database=database)
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")
    con.execute("INSTALL spatial;")
    con.execute("LOAD spatial;")
    return con


def create_places_with_categories_view_and_export(
    s3_places_path: str,
    s3_categories_path: str,
    output_path: str = 'data\output.geoparquet',
    db_path: str = ':memory:'
):
    """
    Creates a DuckDB view joining places and categories from S3 parquet files and exports the result to a GeoParquet file.
    Args:
        s3_places_path (str): S3 path to places parquet files.
        s3_categories_path (str): S3 path to categories parquet file.
        output_path (str): Output file path for GeoParquet export.
        db_path (str): DuckDB database path (default: in-memory).
    """
    con = duckdb.connect(database=db_path)
    try:
        # Load required extensions
        con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;")

        # Create the view
        con.execute(f"""
        CREATE OR REPLACE VIEW places_with_categories AS
        WITH places AS (
            SELECT
                DISTINCT UNNEST(P.fsq_category_ids) as fsq_category_id,
                name,
                postcode,
                address,
                region,
                ST_Point(longitude, latitude) AS geom
            FROM read_parquet('{s3_places_path}') AS P
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND country='IN'
        ),
        places_with_categories AS (
            SELECT
                P.name AS name,
                C.level1_category_name AS category_level_1,
                C.level2_category_name AS category_level_2,
                postcode,
                address,
                region,
                P.geom
            FROM places AS P
            JOIN read_parquet('{s3_categories_path}') AS C
            ON P.fsq_category_id = C.category_id
        )
        SELECT
            name,
            category_level_1,
            category_level_2,
            address,
            region,
            postcode,
            geom
        FROM places_with_categories;
        """)

        # Export the view to GeoParquet
        con.execute(f"COPY (SELECT * FROM places_with_categories) TO '{output_path}' WITH (FORMAT PARQUET, CODEC ZSTD);")
    finally:
        con.close()



if __name__ == "__main__":

    s3_places_path = 's3://fsq-os-places-us-east-1/release/dt=2025-09-09/places/parquet/places-*.zstd.parquet'
    s3_categories_path = 's3://fsq-os-places-us-east-1/release/dt=2025-09-09/categories/parquet/categories.zstd.parquet'

    create_places_with_categories_view_and_export(
        s3_places_path=s3_places_path,
        s3_categories_path=s3_categories_path,
        output_path='data/output.geoparquet'
    )