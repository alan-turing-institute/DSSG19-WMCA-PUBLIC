#################################################i############
# Executes various SQL and Python files to run ETL pipeline #
#############################################################

import os
import settings
from etl.load_raw import load_data_dict, load_text, load_gis, load_osm
import etl.api_load_data as api_load_data
from utils import *


def run():
    """
    Execute Extract-Transform-Load (ETL) process.
    Note: This entire process will take several hours to complete.

    Parameters
    ----------
    ROOT_FOLDER : str
        Directory where the project is stored locally.
    DATA_FOLDER : str
        Directory where the raw data are stored locally.
    
    Returns
    -------
    None
    """
    
    # Get environment folders
    ROOT_FOLDER = settings.get_root_dir()
    DATA_FOLDER = os.path.join(ROOT_FOLDER, 'data/')
    SQL_FOLDER = os.path.join(ROOT_FOLDER, 'sql/')

    # Data files to be loaded
    data_config = os.path.join(ROOT_FOLDER, 'config/base/data_files.yaml')
    
    # Get PostgreSQL database credentials 
    psql_credentials = settings.get_psql()

    # Create SQLAlchemy engine from database credentials
    engine = create_connection_from_dict(psql_credentials, 'postgresql')

    ## ---- CREATE SCHEMAS ----

    print("Creating schemas")
    execute_sql(os.path.join(SQL_FOLDER,'create_schemas.sql'), engine, read_file=True)

    ## ---- CREATE TABLES WITHIN RAW SCHEMA ----
    print("Creating tables")
    execute_sql(os.path.join(SQL_FOLDER, 'create_tables.sql'), engine, read_file=True)

    ## ---- LOAD RAW DATA TO DATABASE ----
    text_dict, gis_dict, osm_file = load_data_dict(data_config)

    # Load CSV file to RAW schema
    print("Loading text files to RAW")
    load_text(DATA_FOLDER, text_dict, engine)

    # Load GIS data to GIS schema
    print("Loading shapefiles to GIS")
    load_gis(DATA_FOLDER, gis_dict, psql_credentials)

    # Load OSM data to RAW schema
    print("Loading OSM data to RAW")
    load_osm(DATA_FOLDER, osm_file, psql_credentials, os.path.join(SQL_FOLDER, 'update_osm_tables.sql'), engine)

    ## ---- CLEAN DATA TO CLEANED SCHEMA ----
    print("Cleaning data")
    execute_sql(os.path.join(SQL_FOLDER, 'clean_data.sql'), engine, read_file=True)

    ## ---- ENTITIZE DATA TO SEMANTIC SCHEMA ----
    print("Entitizing data")
    execute_sql(os.path.join(SQL_FOLDER, 'create_semantic.sql'), engine, read_file=True)

if __name__ == '__main__':
    run()
