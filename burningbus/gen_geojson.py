import sqlalchemy as db
import yaml
from pathlib import Path

def create_connection(ROOT_FOLDER):
    """util function"""
    with open(ROOT_FOLDER + 'config/local/.credentials.yaml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        
    psql_cfg = cfg['postgresql']

    db_url = db.engine.url.URL(drivername='postgresql', \
                 username=psql_cfg['user'], password=psql_cfg['password'], \
                 host=psql_cfg['host'], database=psql_cfg['dbname'])
    
    engine = db.create_engine(db_url)
    conn = engine.connect()
    return conn


def get_model_num(conn, population, poi, metric):
    """ Takes user specifications about the population of interest, POI, 
    and the metric. Returns a model number.

     Parameters
     ----------
     conn : sqlalchemy connection object
         Connection to project database in postgres
     population : str
         Subpopulation of interest
     poi : str
         Points of interest (i.e, hospitals)
    metric : str
        System for measuring connectivity (i.e., aerial distance)

     Returns
     -------
     model_num: int
         Id number of a model for querying

    """
    query = """ SELECT model_id
                FROM model.models
                WHERE population = population
                    AND metric = metric
                    """
    # subsetting for first element gets us the model number                
    model_num = conn.execute(query).fetchone()[0] 
    return(model_num)
    
    
def gen_geojson(conn, model_num):
    """ Queries postgres and returns a geoJSON file with boundary data
    and properties that give us demographics and transit access data.
    
     Parameters
     ----------
     model_num: int
         The number of the model in question

     Returns
     -------
     geoJSON: geoJSON file
         A file where the rows are OAs (the exact number will depend on 
         the query) and the columns are geometry, demographics, and a 
         metric value. 
    
    """
    # path to sql file (model number is currently hardcoded!)
    sql_filename = "/Users/james/Documents/DSSG/DSSG19-WMCA/sql/fetch_geoJSON.sql"    
    # read sql
    query = Path(sql_filename).read_text()
    # query postgres
    geoJSON = conn.execute(query).fetchall()
    return(geoJSON)


def run():
    ROOT_FOLDER = '/Users/james/Documents/DSSG/DSSG19-WMCA/'
    # get connection to postgres
    conn = create_connection(ROOT_FOLDER)
    # get the model number from user input
    model_num = get_model_num(conn, "elderly", "hospitals", "mean_dist_to_hospital_in_5000_m")
    # generate geoJSON
    geoJSON = gen_geojson(conn, model_num)
    print(geoJSON[0])
