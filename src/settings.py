from dotenv import load_dotenv, find_dotenv
import os

def load():
    load_dotenv(find_dotenv())

def get_psql():
    POSTGRES_HOST = os.environ['POSTGRES_HOST']
    POSTGRES_DB = os.environ['POSTGRES_DB']
    POSTGRES_USER = os.environ['POSTGRES_USER']
    POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
    POSTGRES_PORT = os.environ['POSTGRES_PORT']
    
    psql_credentials = {'host': POSTGRES_HOST,
                        'dbname': POSTGRES_DB,
                        'user': POSTGRES_USER,
                        'password': POSTGRES_PASSWORD,
                        'port': POSTGRES_PORT}
    
    return psql_credentials

def get_root_dir():
    ROOT_FOLDER = os.environ['ROOT_FOLDER']
    return ROOT_FOLDER

def get_otp_settings():
    LOAD_BALANCER_HOST = os.environ['LOAD_BALANCER_HOST']
    LOAD_BALANCER_PORT = os.environ['LOAD_BALANCER_PORT']
    NUM_OTPS = os.environ['NUM_OTPS']
    return LOAD_BALANCER_HOST, LOAD_BALANCER_PORT, NUM_OTPS

def get_mapbox_token():
    MAPBOX_TOKEN = os.environ['MAPBOX_TOKEN']
    return MAPBOX_TOKEN


