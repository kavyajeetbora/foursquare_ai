"""
Database utility functions for DuckDB and other DBs.
"""
import duckdb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
import os
from glob import glob
import shutil
from src.utils.logger import logging
import randomname
from time import time

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
    output_path: str = r'data\output.geoparquet',
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
            COPY (
                SELECT
                    name,
                    UNNEST(fsq_category_labels) as category,
                    address,
                    region,
                    postcode,
                    geom
                FROM read_parquet('{s3_places_path}')  WHERE country = 'IN'      
            ) TO '{output_path}' WITH (FORMAT PARQUET, CODEC ZSTD);
        """)

    finally:
        con.close()

def create_vector_db_for_categories(vector_db_dir: str, model_name: str):
    """
    Creates a distinct list of categories from the places parquet files.
    Args:
        s3_places_path (str): S3 path to places parquet files.
    """
    start_time = time() 
    ## 1. First Get all the Distinct Categories from Places
    # Initialize DuckDB connection
    con = duckdb.connect()

    # Load required extensions
    con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;")

    s3_places_path = 's3://fsq-os-places-us-east-1/release/dt=2025-09-09/places/parquet/places-*.zstd.parquet'

    # Execute the SELECT query and create a view
    result = con.execute(f"""
    SELECT
        DISTINCT UNNEST(fsq_category_labels) as category
    FROM read_parquet('{s3_places_path}') WHERE country='IN';
    """).df()

    con.close()

    ## 2. Intialize the Embedding Model
    logging.info("Downloading Embeddings Model   ")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    logging.info("Embeddings Model Downloaded   ")

    ## 3. Create the Vector DB
    logging.info("Creating Embeddings for Categories")

    ## First Create documents
    categories = result['category'].drop_duplicates().tolist()

    documents = [
            Document(
                page_content=cat, metadata={"category_id": i, "source": "foursquare poi"}
            ) for i,cat in enumerate(categories)
        ]

    logging.info(f"Created {len(documents)} documents for categories")

    ## 4. Create the Vector DB into Local Path
    ## Now Store the Embeddings in Vector Store

    

    logging.info("Creating Vector DB Directory if not exists")
    os.makedirs("db", exist_ok=True)

    random_suffix = randomname.get_name()

    persistent_directory = f"{vector_db_dir}/chroma-({random_suffix})"

    ## If already there, delete and create a new one
    for folder in glob(f"{vector_db_dir}/chroma*"):
        if os.path.exists(folder):
            shutil.rmtree(folder)

    os.mkdir(persistent_directory)

    logging.info(f"Created Vector DB Directory at {persistent_directory}")

    logging.info("Creating Vector DB for Categories")
    vector_db = Chroma.from_documents(
        documents=documents,
        collection_name="poi_category_embeddings",
        embedding=embeddings,  # Now LangChain-compatible!
        persist_directory=persistent_directory
    )
    logging.info("Created Vector DB to Disk")

    end_time = time()
    logging.info(f"Time taken to create vector DB: {end_time - start_time} seconds")


def load_vector_db(path, collection_name="poi_category_embeddings", model_name="sentence-transformers/all-MiniLM-L6-v2"):
    if os.path.exists(path):
        # Same embedding model as creation—critical for query consistency
        embedding = HuggingFaceEmbeddings(model_name=model_name)
        
        vector_db = Chroma(
            persist_directory=path,
            collection_name=collection_name,
            embedding_function=embedding
        )
        logging.info(f"Loaded vector DB from {path} with collection {collection_name}")
        return vector_db
    else:
        logging.error(f"Path {path} not found!")
        return None


if __name__ == "__main__":

    # s3_places_path = 's3://fsq-os-places-us-east-1/release/dt=2025-09-09/places/parquet/places-*.zstd.parquet'
    # s3_categories_path = 's3://fsq-os-places-us-east-1/release/dt=2025-09-09/categories/parquet/categories.zstd.parquet'

    # create_places_with_categories_view_and_export(
    #     s3_places_path=s3_places_path,
    #     s3_categories_path=s3_categories_path,
    #     output_path=r'data/output.geoparquet'
    # )
    start_time = time()

    vector_db_path = r"data\vector_db"
    # create_vector_db_for_categories(vector_db_dir=vector_db_path, model_name="Qwen/Qwen3-Embedding-0.6B")
    vectordbs = glob(f"{vector_db_path}/chroma*")
    if len(vectordbs) > 0:
        logging.info(f"Found existing vector DBs: {vectordbs}")

        vector_db = load_vector_db(path=vectordbs[0], model_name="Qwen/Qwen3-Embedding-0.6B")

        logging.info(f"Vector DB has {vector_db._collection.count()} vectors.")
        
        query = "Find places where I can find Italian food in Gurgaon?"
        results = vector_db.similarity_search(query, k=5)
        for res in results: 
            print(res.page_content)

    print("Time taken: ", time() - start_time, " seconds")