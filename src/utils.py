###########################
# Commonly used functions #
###########################

import pandas as pd
import sqlalchemy as db
import yaml
from pathlib import Path
from datetime import datetime, timedelta, date
from itertools import product
import calendar
import holidays


def load_yaml(filename):
    """
     Returns the contents of a yaml file in a list

     Parameters
     ----------
     filename : string
        The full filepath string '.../.../.yaml' of the yaml file to be loaded

     Returns
     -------
     cfg : dict
        Contents of the yaml file (may be a nested dict)
    """

    with open(filename, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    return cfg


def create_connection(drivername, username, password, host, database, port, echo=False):
    """
    Creates connection to a database from specified parameters

    Parameters
    ----------
    drivername : string
        The driver of the database to connect to e.g. 'postgresql'
    username : string
    password : string
    host : string
    database : string
    port : string

    echo : True, False, or "debug"
        Passing boolean value True prints SQL query output to stdout. 
        Passing "debug" prints SQL query + result set output to stdout. 

    Returns
    -------
    engine : SQLAlchemy engine object
    """

    db_url = db.engine.url.URL(drivername=drivername, username=username, password=password, host=host,
                               database=database, port=port)
    engine = db.create_engine(db_url, echo=echo)
    return engine


def create_connection_from_dict(dictionary, driver):
    """
    Creates connection to a database from parameters given in a dictionary

    Parameters
    ----------
    drivername : string
        The driver of the database to connect to e.g. 'postgresql'
    dictionary : dict
        Dict of parameters (e.g. {'host': host, 'user': user})

    Returns
    -------
    engine : SQLAlchemy engine object
    """

    engine = create_connection(drivername=driver, \
                               username=dictionary['user'], password=dictionary['password'], \
                               host=dictionary['host'], database=dictionary['dbname'], \
                               port=dictionary['port'])

    return engine


def create_connection_from_yaml(yamlfile, driver):
    """
    Creates connection to a database from a yamlfile

    Parameters
    ---------
    yamlfile : string
        The full filepath string of the credentials file
    driver : string
        The driver (e.g. 'postgresql') to lookup in the credentials file

    Returns
    -------
    engine: SQLAlchemy engine object
    """

    cfg = load_yaml(yamlfile)[driver]
    engine = create_connection(drivername=driver, \
                               username=cfg['user'], password=cfg['password'], \
                               host=cfg['host'], database=cfg['dbname'], port=cfg['port'])

    return engine


def copy_text_to_db(src_file, dst_table, engine, mode='append', header=True, sep=','):
    """
    Copy a csv or txt file to a specified database, where the corresponding table has been created
    Parameters
    ----------
    src_file : str
        Path of the source csv file to be copied
    dst_table : str
        Full name of the database table that stores the .csv file , in the form of "schema.table"
    header: boolean
        Whether the csv file has column names in the first row
    sep : str
        File delimiter
    engine : SQLAlchemy engine object
        Connection to the target database
    
    mode : str
        {"append", "replace"}
        Either append to the database table or replace it

    mode : str
        {"append", "replace"}
        Either append to the database table or replace it
    Returns
    -------
    None
    """

    conn = engine.raw_connection()
    cur = conn.cursor()
    # if mode == 'replace':
    #    cur.execute(f"DELETE FROM {dst_table} WHERE TRUE;")
    #    conn.commit()
    with open(src_file, 'r', encoding='ISO-8859-1') as f:
        if header:
            head = 'HEADER'
        else:
            head = ''
        cur.copy_expert(f"COPY {dst_table} FROM STDIN with DELIMITER '{sep}' {head} CSV", f)
    print(f"{src_file} copied to {dst_table}")
    conn.commit()


def execute_sql(string, engine, read_file, print_=False, return_df=False, chunksize=None, params=None):
    """
    Executes a SQL query from a file or a string using SQLAlchemy engine
    Note: Must only be basic SQL (e.g. does not run PSQL \copy and other commands)
    Note: SQL file CANNOT START WITH A COMMENT! There can be comments later on in the file, but for some reason
    doesn't work if you start with one (seems to treat the entire file as commented)

    Parameters
    ----------
    string : string
        Either a filename (with full path string '.../.../.sql') or a specific query string to be executed
        Can include "parameters" (in the form of {param_name}) whose values are filled in at the time of execution
    engine : SQLAlchemy engine object
        To connect to DB
    read_file : boolean
        Whether to treat the string as a filename or a query
    print_ : boolean
        Whether to print the 'Executed query' statement
    return_df : boolean
        Whether to return the result table of query as a Pandas dataframe
    chunksize : int
        Rows will be read in batches of this size at a time; all rows will be read at once if not specified
    params : dict
        In the case of parameterized SQL, the dictionary of parameters in the form of {'param_name': param_value}

    Returns
    -------
    ResultProxy : ResultProxy
        see SQLAlchemy documentation; results of query
    """

    if read_file:
        query = Path(string).read_text()
    else:
        query = string

    if params is not None:
        query = query.format(**params)

    if print_:
        print('Query executed')

    if return_df:
        res_df = pd.read_sql_query(query, engine, chunksize=chunksize)
        return res_df
    else:  # Not all result objects return rows.
        engine.execute(query)


def date_range(start_date, end_date, weekdays=None, exclude_holidays=True):
    """
    Generate a list of all dates within the given period

    Parameters
    ----------
    start_date : datetime.date object
        Starting date of the period
    end_date : datetime.date object
        Ending date of the period
    weekdays : list
        If specified, constrain to these days of the week only, e.g., ['Tuesday', 'Friday']
        
    Returns
    -------
    rng : list
        List of dates in the format of datetime.date
    """
    rng = []
    d = start_date
    while d <= end_date:
        if weekdays is None or list(calendar.day_name)[d.weekday()] in weekdays:
            if not exclude_holidays or d not in holidays.UK():
                rng.append(d)
        d += timedelta(days=1)
    return rng


def time_range(start_time, end_time, unit='m'):
    """
    Generate a list of all timepoints within the given period

    Parameters
    ----------
    start_time : datetime.time object
        Starting time of the period
    end_time : datetime.time object
        Ending date of the period
    unit : string
        Unit of timepoint, supporting hour('h'), minute('m') and second('s')

    Returns
    -------
    rng : list
        List of timepoints in the format of datetime.time object
    """
    unit_dict = {'h': timedelta(hours=1), 'm': timedelta(minutes=1), 's': timedelta(seconds=1)}
    delta = unit_dict[unit]

    rng = []
    t = datetime.combine(date.today(), start_time)
    while t <= datetime.combine(date.today(), end_time):
        rng.append(t.time())
        t += delta
    return rng


# def to_datetime_from_datetime64(date):
#     """
#     Converts a numpy datetime64 object to a python datetime object
#     Input:
#       date - a np.datetime64 object
#     Output:
#       DATE - a python datetime object
#     """
#     timestamp = ((date - np.datetime64('1970-01-01T00:00:00'))
#                  / np.timedelta64(1, 's'))
#     return datetime.utcfromtimestamp(timestamp)


def datetime_range(date_range, time_range):
    """
    Generate a list of all combinations of given dates and timepoints

    Parameters
    ----------
    date_range : list of datetime.date object
    time_range : list of datetime.time object

    Returns
    -------
    rng : list of datetime.datetime object
    """
    rng = []
    for (date, time) in product(date_range, time_range):
        rng.append(datetime.combine(date, time))
    return rng