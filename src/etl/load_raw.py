'''
Loads GIS shapefiles to database
'''

import subprocess
import os
from utils import copy_text_to_db, load_yaml, execute_sql


def load_data_dict(data_config):
    """
    Load mapping information (dictionary) between raw data files to table names in the
    database.

    Parameters
    ----------
    data_config : str
        Path of the config file that stores data dictionaries in yaml.
        This file should contains two dictionaries, one for csv files and one for spatial
        files.

    Returns
    -------
    text_dict : dict
        Data dictionary that maps each raw csv or txt file to its corresponding table name in
        RAW schema of the database, in the form of {'table1.csv': 'table1_alias'}

    gis_dict : dict
        Data dictionary that maps each file directory (containing one .shp file) to its
        corresponding table name in GIS schema of the database, in the form of
        {'dir1': 'dir_alias'}
        
    osm_file : str
        Name of OSM file

    """
    data_dict = load_yaml(data_config)
    text_dict = data_dict['text_dict']
    gis_dict = data_dict['gis_dict']
    osm_file = data_dict['osm_file']
    return text_dict, gis_dict, osm_file


def load_text(DATA_DIR, data_dict, engine):
    
    """
    Load csv or txt files to database

    Parameters
    ----------
    DATA_DIR : str
        Directory where the raw data are stored locally
    
    data_dict: str
        Data dictionary that maps each raw csv or txt file to its corresponding table name in
        RAW schema of the database, in the form of {'table1.csv': 'table1_alias'}
    
    engine : SQLAlchemy engine object
        Connection to the target database
    
    Returns
    -------
    None
    """
    
    for textfile in data_dict.keys():

        infile = os.path.join(DATA_DIR, textfile)
        outtable = 'raw.' + data_dict[textfile]

        if textfile.endswith('.csv'):
            sep = ','
        elif textfile.endswith('.txt'):
            sep = ','
        # for some reason even these text files only worked uploading with ',' delimiter

        copy_text_to_db(src_file=infile, dst_table=outtable, engine=engine, sep=sep)


def load_shp_to_db(src_dir, dst_table, credentials):

    """
    Load shapefiles to database

    Parameters
    ----------
    src_dir : str
        Directory where GIS file directories (each containing one .shp file only) are stored locally
    
    dst_table: str
        Full name of the database table that stores the .shp file , in the form of "schema.table"
    
    credentials : dict
        Dictionary of elements of database credentials including host, user, dbname and password
    
    Returns
    -------
    None
    """

    # Must be INSIDE the same directory as the .shp file in order to pull other files
    # Go into each directory and get the shapefile

    os.chdir(src_dir)

    for source, dirs, files in os.walk(src_dir):
        for file in files:
            if file[-3:] == 'shp':
                print("Found Shapefile")
                shapefile = file
    
                command = f'''ogr2ogr -overwrite -f "PostgreSQL" PG:"host={credentials['host']} user={credentials['user']} \
                dbname={credentials['dbname']} password={credentials['password']}" {shapefile} -nln {dst_table} -nlt \
                PROMOTE_TO_MULTI'''

                print(f"Uploading file {shapefile}")
                subprocess.call(command, shell=True)
                print("Done")


def load_gis(DATA_DIR, data_dict, credentials_dict):

    """
    Load gis (shape) files to database

    Parameters
    ----------
    DATA_DIR : str
        Directory where the raw data are stored locally
    
    data_dict: dict
        Data dictionary that maps each file directory (containing one .shp file) to its 
        corresponding table name in GIS schema of the database, in the form of
        {'dir1': 'dir_alias'}
    
    credentials_dict:
        Dict of the database credentials
    
    Returns
    -------
    None
    """
    
    for dir in data_dict.keys():
        indir = os.path.join(DATA_DIR, dir)
        outtable = 'gis.' + data_dict[dir]
        load_shp_to_db(indir, outtable, credentials_dict)
        

def load_osm(DATA_DIR, src_file, credentials_dict, sql_file, engine):
    """
    Load OpenStreetMap data to database

    Parameters
    ----------
    DATA_DIR : str
        Directory where raw data are stored locally
    src_file : str
        Name of .pbf file
    credentials_dict : dict
        Dictionary of credential elements
    sql_file : str
        Name of SQL file for updating OSM data
    engine : SQLAlchemy engine object

    Returns
    -------
    None

    """

    os.chdir(DATA_DIR)
            
    # Automatically uploads to PUBLIC schema
    command = 'osm2pgsql --slim --hstore -d ' + credentials_dict['dbname'] \
                + ' -H ' + credentials_dict['host'] + ' -P ' + credentials_dict['port'] \
                + ' -U ' + credentials_dict['user'] + ' ' + src_file
    print(f"Uploading file {src_file}")
    subprocess.call(command, shell=True)
    print("Done")

    # Rename the files and move to RAW schema
    execute_sql(sql_file, engine, read_file=True)
