import sqlalchemy as db
import pandas as pd
import yaml
import numpy as np
import os

def create_connection():
    with open(ROOT_FOLDER + 'config/local/.credentials.yaml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        
    psql_cfg = cfg['postgresql']

    db_url = db.engine.url.URL(drivername='postgresql', \
                 username=psql_cfg['user'], password=psql_cfg['password'], \
                 host=psql_cfg['host'], database=psql_cfg['dbname'])
    
    engine = db.create_engine(db_url)
    conn = engine.connect()
    return conn
         
def grab_data(conn, schema, table, columns):
    """ Obtain data from Postgres. 
    :param schema: name of schema in db
    :param table: name of table in schema
    :param columns: list of column names (not working yet)
    :type schema: str
    :type table: str
    :return: data from data
    :rtype: two-dimensional list where each list is as long as the 
    number of columns passed in. 
    """
    metadata = db.MetaData(conn, schema=schema)
    table = db.Table(table, metadata, autoload=True, autoload_with=conn)
    select_query = db.select(
        [table.c.mean_dist_to_hosp, table.c.elderly_pop]) # this is still hard-coded
    ResultProxy = conn.execute(select_query)
#   df = pd.DataFrame(ResultProxy.fetchall())
    arr = [[r['mean_dist_to_hosp'],r['elderly_pop']] for r in ResultProxy]
    return(arr)

def generate_histogram(arr, bins):
    """ Convert data into histogram model. 
    :param arr: a two-dimensional list of distances and counts
    :param bins: the number of bins to divide the data into
    :type bins: int
    :return: the counts of individuals in the bins
    :rtype: list
    """
    exploded_l = []
    # loop through list duplicating the distance for every individual
    # in the geographical area
    for pair in arr:
        exploded = [[pair[0]] * pair[1]]
        exploded_l.extend(exploded)
    # flatten the list of lists
    exploded_l = [item for sublist in exploded_l for item in sublist]
    # convert to histogram
    binned = np.histogram(exploded_l, bins)            
    return(binned)

def format_for_write(bin_count, binned, description):
    """ Convert data to df format as preparation for writing to Postgres.
    :param bin_count: Number of bins in histogram model
    :type bin_count: int
    :param binned: Counts and minimums for the bins
    :type binned: two numpy arrays of the same length
    :param description: Description of the model
    :type description: str
    """
    df = pd.DataFrame({'bin_count': bin_count,
                       'bin_minimums': [binned[1].tolist()], 
                       'subgroup_pop': [binned[0].tolist()], 
                       'description': description})
    return(df)
    
def write_hist_to_db(conn, df, table_to_write):
    """ Writes data to postgres
    :param conn: sqlalchemy connection object
    :param df: distribution data to write
    :type df: pandas dataframe
    :param table_to_write: name of table to write to
    """
    df.to_sql(table_to_write, conn, schema='results', \
              if_exists='append', index = False)
    
# set some vars
ROOT_FOLDER = "/Users/james/Documents/DSSG/DSSG19-WMCA/" # temporary fix
#ROOT_FOLDER = os.environ['ROOT_FOLDER'] # will work soon
description = "Mean distance from OA centroid to hospitals within 5000 meters."
bin_count = 10
columns = ['mean_dist_to_hosp', 'elderly_pop']
table_to_write = 'model_1_distribution'

# run functions
conn = create_connection()
arr = grab_data(conn, 'results', 'model_1_results', columns)
binned = generate_histogram(arr, bin_count) 
df = format_for_write(bin_count, binned, description)
write_hist_to_db(conn, df, table_to_write)
