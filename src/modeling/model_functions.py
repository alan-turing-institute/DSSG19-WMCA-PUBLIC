import time
import subprocess
import multiprocessing
import numpy as np
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import os
import modeling.open_trip_planner as otp
from utils import *
from random import seed, sample
from datetime import datetime, timedelta


def create_timestamps(time_defs, time_strata, n_timepoints, engine, suffix, rseed = 999):
    """
    Sample time points from strata (time segments) and write to MODEL.timestamps
    Example:
        time_seg              |  day         |   time
        +++++++++++++++++++++++++++++++++++++++++++++++
        Weekday inter-peak    |  2019-07-02  |   12:00pm

    Parameters
    ----------
    time_defs : dict
        Definitions of our strata taxonomy, mapping each dimension of the strata to interpretable time strings
        Example:
            {'time_of_day':
                {'peak': ['8:00-9:00'], 'off-peak': ['11:00-15:00']},
            'day_of_week':
                {'weekday': ['Tuesday'], 'saturday': ['Saturday']}}
    
    time_strata : dict
        Dict of strata (time segments), each being a dict of values on foregoing dimensions and the number of
        samples
        Example:
            {'Weekday (AM peak)': {'time_of_day': 'peak', 'day_of_week': 'weekday', 'n_sample': 50}, ...}
    
    n_timepoints : int
        Default number of samples for each stratum, if specified
    
    engine : a SQLAlchemy engine object

    suffix : str
        suffix (if any) to append to name 'MODEL.timestamps'

    rseed : int
        Random seed for random sampling

    Returns
    ----------
    None
    """
    seed(rseed)
    # if mode == 'append':
    #     strata_exist = pd.read_sql_query(sql=f"SELECT DISTINCT stratum FROM model.timestamps", con=engine)[
    #         'stratum'].tolist()
    #     for st in strata_exist:
    #         time_strata.pop(st, None)

    # start by unpacking inputs into datetimes
    start_date_str = time_defs.get('term')['start_date']
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    if start_date <= datetime.now().date():
        start_date = datetime.now().date() + timedelta(days=1)

    end_date_str = time_defs.get('term')['end_date']
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Create list to hold all table rows
    timestamps = []

    # Loop through all strata and create timepoints (at minute level) for each stratum
    for stratum, values in time_strata.items():
        print(f'Sampling times for "{stratum}"')
        if 'n_sample' in values.keys():
            n = values['n_sample']
        else:
            n = n_timepoints
        time_of_day = time_defs.get('time_of_day')[values['time_of_day']]
        day_of_week = time_defs.get('day_of_week')[values['day_of_week']]

        # All dates in the stratum
        days_in_stratum = date_range(start_date, end_date, day_of_week)

        # All time (minutes) in the stratum
        times_in_stratum = []
        for hours in time_of_day:
            start_time_str, end_time_str = hours.split('-')
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            times_in_stratum += time_range(start_time, end_time)

        # Cartesian product of dates and times -> all time points in the stratum for sampling
        timestamps_in_stratum = datetime_range(days_in_stratum, times_in_stratum)

        # Sample specified number of timepoints
        timestamps_sampled = sample(timestamps_in_stratum, n)

        for ts in timestamps_sampled:
            date = ts.strftime('%Y-%m-%d')
            time = ts.strftime('%H:%M')
            ts_dict = {'stratum': stratum, 'date': date, 'time': time}
            timestamps.append(ts_dict)

    df = pd.DataFrame(timestamps)
    df.to_sql(f'timestamps{suffix}', engine, schema='model', index=False, if_exists='replace')
    print(f'Sampled timestamps saved to model.timestamps{suffix}')

    
def create_k_poi(sql_dir, k_poi, poi_dict, engine, suffix):
    """
    For each OA and each type of point of interest (POI), select K nearest spots (by aerial distance) and write the
    results to MODEL.k_poi

    Parameters
    ----------
    sql_dir : string
        Directory that stores create_model_k_poi.sql

    k_poi : int
        Default # of nearest POIs to compute

    poi_dict : dict
        Keys are POI types as in the "type" column in semantic.poi; for each key, value is the k specific to that
        type, if specified, otherwise use the default k
        Example:
            Hospital: 3
            Job Centre:
    engine: SQLAlchemy engine object
    
    suffix : str
        Suffix to append to name 'MODEL.K_poi' as the table name

    Returns
    ----------
    None
    """
    sql_file = os.path.join(sql_dir, 'create_model_k_poi.sql')

    poi_types = list(poi_dict.keys())
    poi_Ks = [poi_dict[poi] or k_poi for poi in poi_dict]

    params = {'poi_types': str(poi_types), 'poi_Ks': str(poi_Ks), 'suffix': suffix}
    execute_sql(sql_file, engine, read_file=True, params=params)
    print(f'K nearest POIs saved to model.k_poi{suffix}')


def create_trips(sql_dir, engine, suffix, mode='replace'):
    """
    Configure trip info for each OTP query and save to MODEL.trips

    Parameters
    ----------
    sql_dir : string
        Directory that stores create_model_trips.sql and append_model_trips.sql

    engine: a SQLAlchemy engine object
    
    suffix : str
        Suffix to append to name 'MODEL.trips' as the table name

    mode : str
        If 'replace', overwrite existing MODEL.trips; if 'append', append to that existing table

    Returns
    ----------
    None
    """

    if mode == 'replace':
        sql_file = os.path.join(sql_dir, 'create_model_trips.sql')
    if mode == 'append':
        sql_file = os.path.join(sql_dir, 'append_model_trips.sql')
    params = {'suffix': suffix}
    execute_sql(sql_file, engine, params=params, read_file=True)
    print(f'Trips info saved to MODEL.trips{suffix}')


def compute_populations(sql_dir, populations, engine):
    """
    Compute population statistics, saved to RESULTS.populations
    Example:
           oa  	| population1 | population2
        ++++++++++++++++++++++++++++++++++++
            A	|  	  34      |      28

    Parameters
    ----------
    sql_dir : string
        Directory that stores create_model_trips.sql and append_model_trips.sql
    
    populations : dict
        Dict of populations, where each key is the population name with values being columns in SEMANTIC.oa mapped
        to that population
        Example:
            elderly:
                - age_75_to_84
                - age_85_to_89
            disabled:
                - disability_severe
                - disability_moderate
                
    engine: a SQLAlchemy engine object

    Returns
    ----------
    None
    """

    params = {}

    ## Write FEATURE.pop
    pop_col_defs = []
    pop_list = list(populations.keys())
    # get the right column aggregation string for each population
    # e.g. 'COALESCE(disability_severe)+COALESCE(disability_moderate) as disabled'
    for pop in pop_list:
        cols = [f"COALESCE({col}, 0)" for col in populations[pop]]
        pop_col_defs.append('+'.join(cols) + ' as ' + pop)
    # join the strings
    params['pop_col_defs'] = ', '.join(pop_col_defs)

    params['pop_col_names'] = str(pop_list)
    params['pop_cols'] = ', '.join(pop_list)

    sql_file = os.path.join(sql_dir, 'create_results_populations.sql')
    execute_sql(sql_file, engine, read_file=True, params=params)
    print('OA-level demographics saved to RESULTS.populations')


def compute_trips(id_, host_url, offset, limit, sql_dir, psql_credentials, csv_dir, suffix, chunksize):
    """
    Compute query result from Open Trip Planner and save to RESULTS.trips (for example see Google Docs) for each given
    trip, defined by the following attributes/parameters:
        1. OA ID
        2. POI ID
        3. Timestamp (date + time)
    The function does the following:
        1. Loop: Read `chunksize` rows of MODEL.trips into memory, generate corresponding OTP queries
        2. Run the queries and save results to `results.csv`
        3. Save `results.csv` back to RESULTS.trips

    Parameters
    ----------
    id_ : int
        The id number of the portion of the trips table that is being read (e.g. if 6 OTP's are available, we'd split into 6 ID numbers)
    host_url : str
        Base url (of local server) for an OTP query
        Example: 'http://localhost:8080'
    offset : int
        Number of rows to offset, to begin portion {id_} of the table
    limit : int
        Number of rows to limit query to. {offset} + {limit} gives the end trip number of the table
    sql_dir : str
        Directory that stores query_trip_info.sql
    psql_credentials : dict
        Dictionary of PSQL credentials in order to create SQLAlchemy engine
    csv_dir : str
        Directory to save results in csv formats
    suffix : str
        Suffix to append to 'results.trips' as the table name
    chunksize: int
        Rows will be read in batches of this size at a time; all rows will be read at once if not specified

    Returns
    -------
    None

    """

    print(f"{id_} on {host_url} for offset {offset} limit {limit}")

    query_sql_file = os.path.join(sql_dir, 'query_trip_info.sql')
    params = {'suffix': suffix, 'limit': limit, 'offset': offset}
    engine = create_connection_from_dict(psql_credentials, 'postgresql')

    count = 1

    # We chunk up the portion received in order to not crash a DF's memory
    for chunk in execute_sql(query_sql_file, engine, read_file=True, return_df=True, params=params,
                             chunksize=chunksize):
        # Get OTP response
        print(f"Getting response from Chunk {count} on OTP {host_url}, for results.trip{suffix}{id_}")
        chunk['response'] = chunk.apply(lambda row: otp.request_otp(host_url, row.oa_lat, row.poi_lat, row.oa_lon,
                                                                    row.poi_lon, row.date, row.time), axis=1)

        # Parse OTP response
        chunk[["departure_time", "arrival_time", "total_time", "walk_time", "transfer_wait_time", "initial_wait_time",
               "transit_time", "walk_dist", "transit_dist", "total_dist", "num_transfers", "fare"]] = chunk.apply(
            lambda row: otp.parse_response(row.response, row.date, row.time), axis=1, result_type="expand")
        chunk = chunk[["trip_id", "departure_time", "arrival_time", "total_time", "walk_time", "transfer_wait_time",
                       "initial_wait_time", "transit_time", "walk_dist", "transit_dist", "total_dist",
                       "num_transfers", "fare"]]
        chunk.num_transfers = chunk.num_transfers.astype(pd.Int16Dtype())
        chunk.set_index('trip_id', inplace=True)

        # Write response to CSV
        print(f"Writing response to CSV from chunk {count} on OTP {host_url}, for results.trip{suffix}{id_}")
        chunk.to_csv(os.path.join(csv_dir, f"trips{suffix}{id_}.csv"), mode='a', header=False)
        count += 1

    # Copy CSV with this portion to DB
    print(f"Copying csv's to db for results.trips{suffix}{id_}")
    copy_text_to_db(os.path.join(csv_dir, f"trips{suffix}{id_}.csv"), f'results.trips{suffix}', engine, mode='append',
                    header=False)

    # Update the model trips table so we know these trips have been computed, if we ever re-run the pipeline with "append" mode
    update_sql_file = os.path.join(sql_dir, 'update_computed_model_trips.sql')
    execute_sql(update_sql_file, engine, read_file=True, params=params)


def split_trips(host, port, num_splits, sql_dir, csv_dir, engine, psql_credentials, suffix, mode, chunksize):
    """
    Parameters
    ----------
    host : str
        Host IP address e.g. '0.0.0.0'
    port : str
        Port number of load balancer e.g. '8888'
    num_splits : int
        The number of times we want to split MODEL.trips (in practice, corresponds to number of OTP's)
    sql_dir : str
        Directory where SQL files are stored
    csv_dir : str
        Directory where result CSVs are stored
    engine : SQLAlchemy engine object
    psql_credentials : dict
        Dictionary of PSQL credentials
    suffix : str
        Suffix (if any) to append to table names
    mode : str
        If 'replace', overwrite existing RESULTS.trips; if 'append', append to that existing table
    chunksize : int
        Size of chunks to read and write from OTP, in compute_trips
        (Our heuristic is chunksize=10000 as this is how much DF memory will take without crashing)

    Returns
    -------
    None
    
    """

    # Set up 
    params = {'suffix': suffix}

    # Str to Int
    num_splits = int(num_splits)

    host_urls = [f"http://{host}:{port}"] * num_splits

    num_trips = \
        execute_sql(f"SELECT count(*) FROM model.trips{suffix};", engine, read_file=False, return_df=True)[
            'count'].values[
            0]  # execute sql query to get count of model.trips table
    step_size = int(np.ceil(num_trips / num_splits))  # number of rows to send to each otp
    offsets = np.arange(0, num_trips, step_size)
    limits = [step_size] * num_splits

    # TODO: maybe change the data inputs below later, a little hacky

    data = np.zeros(shape=(num_splits, 9), dtype=object)

    data[:, 0] = np.arange(1, num_splits + 1)  # ID's
    data[:, 1] = host_urls  # host_urls
    data[:, 2] = offsets  # offsets
    data[:, 3] = limits  # limits
    data[:, 4] = [sql_dir] * num_splits  # constant sql dir
    data[:, 5] = [psql_credentials] * num_splits  # constant credentials (since can't pass an eng directly)
    data[:, 6] = [csv_dir] * num_splits  # constant results dir
    data[:, 7] = [suffix] * num_splits  # constant suffix
    data[:, 8] = [chunksize] * num_splits  # constant chunksize

    data = data.tolist()

    # If replacing table,
    if mode == 'replace':

        # Set computed back to 0 for this model trips
        # This should work even if first time running this result, because model.trips should have
        # already been created.
        execute_sql(f"UPDATE model.trips{suffix} SET computed=0;", engine, read_file=False)

        # Delete results CSVs
        try:
            subprocess.call(f"rm {csv_dir}trips{suffix}*", shell=True)
        except:  # If first time creating table
            "First time creating table, no CSV's to delete."

        # Destroy existing results.trips table
        create_table_sql_file = os.path.join(sql_dir, 'create_results_trips.sql')
        execute_sql(create_table_sql_file, engine, read_file=True, params=params)

    # Execute queries on separate threads

    start = time.time()

    pool = multiprocessing.Pool(num_splits)
    results = pool.starmap(compute_trips, [tuple(row) for row in data])
    pool.close()

    end = time.time()
    elapsed = end - start

    print(results)
    print("Minutes elapsed {}".format(elapsed / 60.0))


def compute_map_attributes(sql_dir, metrics, engine, suffix):
    """
    Based on RESULTS.trips, generate OA-level travel statistics for maps (for example see Google Docs)
    1. Generate the Cartesian product of OA_ID X POI_type X stratum X metric
       NOTE: create an "all" stratum
    2. Take the median value across all timestamps in a given stratum for each of the K POIs under the POI_type
    3. Choose the value of POI that has the best (smallest) metric value

    Parameters
    ----------
    sql_dir : string
        Directory that stores create_vis_map_attributes.sql

    metrics : list
        List of str metrics that we want to include in the map attributes table
        E.g. ['total_time', 'walk_time', 'fare']

    engine: a SQLAlchemy engine object

    suffix : str
        Suffix to append to table names, if any

    Returns
    -------
    None

    """

    # Get the metrics list but without the quotes, for correct SQL file formatting
    # i.e. metric_arr should look like ['total_time', 'fare']
    # but value_arr should look like [total_time, fare]
    metric_arr = metrics
    value_arr = str(metrics).replace("'", "")
    metrics_in_second = str(list(filter(lambda x: 'time' in x, metrics))).replace('[', '(').replace(']', ')')
    
    sql_file = os.path.join(sql_dir, 'create_vis_map_attributes.sql')
    params = {'metric_arr': metric_arr, 'value_arr': value_arr, 'metrics_in_second': metrics_in_second, 'suffix': suffix}

    execute_sql(sql_file, engine, read_file=True, params=params)
    print(f'Data for mapping saved to VIS.map_attributes{suffix}')


def compute_histograms(engine, suffix):
    """
    Based on RESULTS.map_attributes, generate data table for histograms (OA-level demographics,
    OA-level access and individual-level access) and save to VIS.histograms_oa_population, VIS.histograms_oa_access,
    VIS.histograms_individual_access respectively

    Parameters
    ----------
    engine: a SQLAlchemy connection object
    
    Returns
    -------
    None

    """
    def compute_bin_centers(hist_array, median=False):
        hist_array = np.asarray(hist_array)
        hist_array = hist_array[~np.isnan(hist_array)]
        counts, bins = np.histogram(hist_array, bins='auto', range=(hist_array.min(), hist_array.max()))
        centers = (bins[:-1] + bins[1:]) / 2
        cut_off = np.mean(hist_array) + (3 * np.std(hist_array))
        if median:
            return counts.tolist(), centers.tolist(), cut_off, np.median(hist_array)
        else:
            return counts.tolist(), centers.tolist(), cut_off

    def compute_individual_hist_vectors(count, value):
        hist_vector = []
        for i in range(len(value)):
            x = [value[i]] * count[i]
            hist_vector.extend(x)
        return hist_vector

    pop_histogram_table = pd.DataFrame(
        columns=['population', 'pop_vector', 'bin_counts', 'bin_centers', 'outlier_cutoff'])
    oa_histogram_table = pd.DataFrame(
        columns=['poi_type', 'stratum', 'metric', 'access_vector', 'bin_counts', 'bin_centers', 'outlier_cutoff'])

    # Compute population histograms and append to dataframe
    df_population = pd.read_sql_table('populations', engine, schema='results')
    grouped_population = df_population.groupby('population')
    for name, group in grouped_population:
        bin_counts, bin_centers, cut_off = compute_bin_centers(group['count'])
        pop_histogram_table = pop_histogram_table.append(
            {'population': name, 'pop_vector': group['count'], 'bin_counts': bin_counts, 'bin_centers': bin_centers,
             'outlier_cutoff': cut_off},
            ignore_index=True)

    # Compute oa histograms and append to dataframe
    df_map_attr = pd.read_sql_table('map_attributes'+suffix, engine, schema='vis')
    grouped_map_attr = df_map_attr.groupby(['poi_type', 'stratum', 'metric'])
    for name, group in grouped_map_attr:
        bin_counts, bin_centers, cut_off = compute_bin_centers(group['value'])
        oa_histogram_table = oa_histogram_table.append(
            {'poi_type': name[0], 'stratum': name[1], 'metric': name[2], 'access_vector': group['value'],
             'bin_counts': bin_counts,
             'bin_centers': bin_centers, 'outlier_cutoff': cut_off},
            ignore_index=True)

    # Create individual level dataframe based on cross product of pop dataframe and oa dataframe
    la, lb = len(pop_histogram_table[['population', 'pop_vector']]), len(
        oa_histogram_table[['poi_type', 'stratum', 'metric', 'access_vector']])
    ia2, ib2 = np.broadcast_arrays(*np.ogrid[:la, :lb])
    ind_histogram_table = pd.DataFrame(np.column_stack(
        [pop_histogram_table[['population', 'pop_vector']].values[ia2.ravel()],
         oa_histogram_table[['poi_type', 'stratum', 'metric', 'access_vector']].values[ib2.ravel()]]))
    ind_histogram_table.columns = ['population', 'pop_vector', 'poi_type', 'stratum', 'metric', 'access_vector']
    ind_histogram_table['bin_counts'] = None
    ind_histogram_table['bin_centers'] = None
    ind_histogram_table['outlier_cutoff'] = None
    ind_histogram_table['median'] = None

    # Compute individual level histograms
    for index, row in ind_histogram_table.iterrows():
        hist_array = compute_individual_hist_vectors(row.pop_vector.values.tolist(), row.access_vector.values.tolist())
        bin_counts, bin_centers, cutoff, median = compute_bin_centers(hist_array, median=True)
        ind_histogram_table.at[index, 'bin_counts'] = bin_counts
        ind_histogram_table.at[index, 'bin_centers'] = bin_centers
        ind_histogram_table.at[index, 'outlier_cutoff'] = cutoff
        ind_histogram_table.at[index, 'median'] = median

    pop_histogram_table.drop(['pop_vector'], axis=1, inplace=True)
    oa_histogram_table.drop(['access_vector'], axis=1, inplace=True)
    ind_histogram_table.drop(['pop_vector', 'access_vector'], axis=1, inplace=True)

    # write dataframes to DB
    pop_histogram_table.to_sql('histograms_oa_population'+suffix, con=engine, schema='vis',
                               if_exists='replace', index=False,
                               dtype={'bin_counts': postgresql.ARRAY(postgresql.FLOAT),
                                      'bin_centers': postgresql.ARRAY(postgresql.FLOAT)})
    oa_histogram_table.to_sql('histograms_oa_access'+suffix, con=engine, schema='vis',
                              if_exists='replace', index=False,
                              dtype={'bin_counts': postgresql.ARRAY(postgresql.FLOAT),
                                     'bin_centers': postgresql.ARRAY(postgresql.FLOAT)})
    ind_histogram_table.to_sql('histograms_individual_access'+suffix, con=engine, schema='vis',
                               if_exists='replace', index=False,
                               dtype={'bin_counts': postgresql.ARRAY(postgresql.FLOAT),
                                      'bin_centers': postgresql.ARRAY(postgresql.FLOAT)})

def compute_scoreboard(engine, suffix):
    """
    Create a "scoreboard" table that compares the overall access across demographic groups for any user-specified
    point of interest, and write to VIS.scoreboard

    Parameters
    ----------
    engine: a SQLAlchemy engine object

    suffix : str
        Suffix to append to table names, if any

    Returns
    -------
    None
    """
    get_res_sql = (
        f"SELECT population, poi_type, metric, median "
        f"FROM vis.histograms_individual_access{suffix} "
        f"WHERE stratum='All times'"
    )
    res = execute_sql(get_res_sql, engine, read_file=False, return_df=True)
    scoreboard = pd.pivot_table(res, values='median', index=['population', 'poi_type'], columns=[
        'metric']).reset_index()
    scoreboard.to_sql('scoreboard'+suffix, engine, schema='vis', if_exists='replace')
