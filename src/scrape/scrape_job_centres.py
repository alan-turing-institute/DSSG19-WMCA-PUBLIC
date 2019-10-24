import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from selenium import webdriver
import time
import pandas as pd
from utils import load_yaml, create_connection, create_connection_from_yaml
import scrape_utils


def scrape_job_centres(driver, pcds):
    """
    Scrapes the UK gov centre locator to create a table with a list of job centres
    and their postcodes.
    
    Parameters
    ---------
    pcd : str
    
    Returns
    --------
    a fixed string
    
    """
    result_table = pd.DataFrame(columns=['residence_pcd',
                                         'residence_oa',
                                         'name',
                                         'pcd'])

    for idx, pcd in pcds.iterrows():
        driver.get("https://find-your-nearest-jobcentre.dwp.gov.uk/")
        inputElement = driver.find_element_by_id("postcode")
        inputElement.send_keys(pcd['pcd'])
        inputElement = driver.find_element_by_name("submit").click()

        for row in driver.find_elements_by_css_selector("tbody"):
            cell = row.find_elements_by_tag_name("tr")[3]
            name = cell.text.partition('\n')[0][15:]
            postcode = cell.text[-7:]
            print(name, postcode)
            result_table = result_table.append({'residence_pcd': pcd['pcd'],
                                                'residence_oa': pcd['oa11'],
                                                'name': name,
                                                'pcd': postcode}, ignore_index=True)
            driver.find_elements_by_xpath("//*[contains(text(), 'Finish')]")
            time.sleep(.05)

    return result_table


# Create a sqlalchemy connection.send_keys(Keys.RETURN)
james_cred = '/Users/james/Documents/DSSG/DSSG19-WMCA/config/local/.credentials.yaml'
conn = create_connection_from_yaml(james_cred, 'postgresql')

pcd_names = scrape_utils.get_pcd_names_from_sample(conn, 1000)
pcd_names['pcd'] = pcd_names['pcd']

driver = scrape_utils.launch_selenium()
result = scrape_job_centres(driver, pcd_names)
result.to_csv('/Users/james/Documents/NCDS/DSSG/wmca/POI/job_centres_sample.csv')

uniques = result.drop_duplicates(['name', 'job_centre_pcd'])[['name', 'job_centre_pcd']]
uniques.to_csv('/Users/james/Documents/NCDS/DSSG/wmca/POI/job_centres.csv')
