from selenium import webdriver
import pandas as pd

def get_pcd_names_from_sample(conn, n):
    """
    Create a dataframe of pcd info. The intention behind the sampling
    is that, because there are 85k postcodes in west midlands, we
    don't need to query for each one. A sample will give us
    what we need.

    Parameters
    ---------
    eng : sqlalchemy engine object
    n : int
        The number of postcodes to sample to capture all
        objects for scraping.

    Returns
    --------
    A pandas dataframe with n rows, and columns for postcodes and oas.
    """
    query = f'''select pcd, oa11 from semantic.pcd order by random() limit {n}'''
    ResultProxy = conn.execute(query)
    df = pd.DataFrame(ResultProxy.fetchall())
    df.columns = ResultProxy.keys()
    return df


def launch_selenium():
    """
    Creates a selenium driver, and opens a Chrome browser.

    Requires
    --------
    A selinium driver for chrome.
    See: https://sites.google.com/a/chromium.org/chromedriver/downloads

    Returns
    --------
    A selenium driver object
    """
    driver = webdriver.Chrome("/Users/james/Downloads/chromedriver")
    return driver