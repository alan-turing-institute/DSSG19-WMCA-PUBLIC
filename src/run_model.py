'''
    Loads a number of experiments we want to run, and sets up pipeline to run them all
'''

import os
import settings
from modeling import model_functions
from utils import load_yaml, create_connection_from_dict


def run(mode='replace', suffix='', chunksize=10000):
   
    """
    Runs the end-to-end pipeline (depends on ETL completion)

    Parameters
    ----------
    mode : str
        If 'replace', overwrite existing results; if 'append', append to existing results
    suffix : str
        Suffix if any to append to tables (for testing purposes)
    chunksize : int
        Chunk size (when writing queries - the max number of rows we think a DF can hold in memory without crashing)
    
    Returns
    -------
    None

    """

    ######## Prepare everything needed for the model ########
    
    # Load environment variables 
    settings.load()

    # Get folders
    ROOT_FOLDER = settings.get_root_dir()
    SQL_FOLDER = os.path.join(ROOT_FOLDER, 'sql/')
    RESULTS_FOLDER = os.path.join(ROOT_FOLDER, 'results/')
    
    # Get PostgreSQL database credentials
    psql_credentials = settings.get_psql()
    
    # Get OTP settings: port number of load balancer and number of OTP containers (i.e. splits)
    host, port, num_splits = settings.get_otp_settings()

    # Load model configuration
    model_config = os.path.join(ROOT_FOLDER, 'config/base/model_config.yaml')
    print('Configure models')
    params = load_yaml(model_config)
    population_dict = params.get('populations')
    poi_dict = params.get('points_of_interest')
    time_defs = params.get('time_defs')
    time_strata = params.get('time_strata')
    hyper_params = params.get('hyper_params')
    metrics = params.get('metrics')
    print('Model parameters loaded')

    # Create SQLAlchemy engine from database credentials
    engine = create_connection_from_dict(psql_credentials, 'postgresql')
    print('Database connected')

    # Sample timestamps and write to MODEL.timestamps
    model_functions.create_timestamps(time_defs, time_strata, n_timepoints=hyper_params.get('n_timepoint'), engine=engine, suffix=suffix)
    # Generate MODEL.k_poi (K-nearest POIs)
    model_functions.create_k_poi(SQL_FOLDER, k_poi=hyper_params.get('k_POI'), poi_dict=poi_dict, suffix=suffix,
                           engine=engine)
    # Configure OTP query parameters and save to MODEL.trips
    model_functions.create_trips(SQL_FOLDER, suffix=suffix, engine=engine, mode=mode)

    ######## Run models and write results to database ########
    # Generate RESULTS.populations
    model_functions.compute_populations(SQL_FOLDER, population_dict, engine)
    # Generate RESULTS.trips
    model_functions.split_trips(host, port, num_splits, SQL_FOLDER, RESULTS_FOLDER, engine, psql_credentials, suffix=suffix, mode=mode, chunksize=chunksize)
    # Generate VIS.map_attributes

    ######## Generate data for visualization and save to database ########
    model_functions.compute_map_attributes(SQL_FOLDER, metrics, engine, suffix=suffix)
    # # Generate three histogram tables:
    # # VIS.histograms_oa_population, VIS.histograms_oa_access, VIS.histograms_individual_access
    model_functions.compute_histograms(engine, suffix=suffix)
    # Generate VIS.scoreboard
    model_functions.compute_scoreboard(engine, suffix=suffix)



if __name__ == '__main__': 
    run()


