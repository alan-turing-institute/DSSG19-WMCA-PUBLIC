import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from utils import load_yaml, create_connection, create_connection_from_yaml
import scrape_utils


def scrape_childcare(driver, pcds):
    """
    Scrapes Ofsted's website to create a table with a list of job centres
    and their postcodes.

    Parameters
    ---------
    driver: obj
        a Selenium driver object
    pcds : pandas dataframe
        a dataframe with a column of postcodes

    Returns
    --------
    res: pandas dataframe
        A dataframe with three columns:

        | origin pcd | name | pcd |

    """
    print(type(pcds))
    res = pd.DataFrame(columns=['origin_pcd', 'origin_oa',
                                'name', 'pcd'])

    for idx, pcd in pcds.iterrows():
        driver.get("https://reports.ofsted.gov.uk/search?q=&level_1_types=2#searchCategories")
        driver.find_element_by_xpath('//input[@id="childcare_and_early_education_3"][@type="checkbox"]').click()
        driver.find_element_by_xpath('//input[@id="childcare_and_early_education_4"][@type="checkbox"]').click()
        inputElement = driver.find_element_by_id("search_location")
        inputElement.send_keys(pcd['pcd'], Keys.RETURN)

        for row in driver.find_elements_by_class_name("search-result"):
            name = row.find_element_by_tag_name("h3").text
            address = row.find_element_by_tag_name("address").text
            address = address.split(', ')
            postcode = address[-1]
            print("\nName: ", name, "\nPostcode: ", postcode)
            res = res.append({'origin_pcd': pcd['pcd'],
                              'name': name,
                              'pcd': postcode}, ignore_index=True)
            driver.find_elements_by_xpath("//*[contains(text(), 'Finish')]")
        time.sleep(.25)

    driver.close()
    return res


def run(chunksize=10):
    """ TODO: docstring
    """
    counter = 0
    james_cred = '/Users/james/Documents/DSSG/DSSG19-WMCA/config/local/.credentials.yaml'
    # Create a sqlalchemy connection
    conn = create_connection_from_yaml(james_cred, 'postgresql')
    path_to_csv = '/Users/james/Documents/NCDS/DSSG/wmca/POI/poi_wm_childcare.csv'
    # Create a starter file to read from
    headers = pd.DataFrame(columns=['name', 'pcd'])
    headers.to_csv(path_to_csv, header=True)

    continue_scraping = True
    while continue_scraping:
        pcd_names = scrape_utils.get_pcd_names_from_sample(conn, chunksize)
        driver = scrape_utils.launch_selenium()

        try:
            all_results = scrape_childcare(driver, pcd_names)
        except: # TODO: figure out what type of error we should catch in this case
            print("an error occurred")
            time.sleep(60)
            continue

        # Drop duplicates
        new_data = all_results.drop_duplicates(['name', 'pcd'])[['name', 'pcd']]
        existing_data = pd.read_csv(path_to_csv)

        first_time_seen = new_data.set_index(['name', 'pcd']).index.isin(existing_data.set_index(['name', 'pcd']).index)
        num_first_time_seen = sum(~first_time_seen)
        print("New data found: ", num_first_time_seen, "rows")

        if num_first_time_seen == 0:
            print("No new entries in chunk:")
            counter += 1
            if counter > 5:
                continue_scraping = False
        else:
            print("writing to csv")
            combined = pd.concat([new_data, existing_data], axis=0)
            combined = combined.drop_duplicates(['name', 'pcd'])[['name', 'pcd']]
            combined.to_csv(path_to_csv, header=True)


if __name__ == "__main__":
    run()
