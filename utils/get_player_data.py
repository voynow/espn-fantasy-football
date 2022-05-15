from locale import normalize
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import time
import pandas as pd


def create_driver():
    """
    Create driver and load espn fantasy football page
    """
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://fantasy.espn.com/football")

    return driver


def navigate_to_scoring_leaders(driver):
    """
    Find scoring leaders tab from espn fantasy football home page
    """
    navs = driver.find_element(By.CLASS_NAME, 'global-nav-container').find_elements(By.CLASS_NAME, 'sub')

    for item in navs:
        nav_link = item.find_element(By.CLASS_NAME, 'link-text')
        if nav_link.text == 'Scoring Leaders':
            nav_link.click()
            time.sleep(5)
            break

def collect_table_metadata(driver):
    """
    Get columns and table length
    """
    header_elements = driver.find_elements(By.CLASS_NAME, "header")
    columns = [element.text for element in header_elements]
    if 'Scoring Leaders' in columns:
        columns.remove('Scoring Leaders')

    player_elements = driver.find_elements(By.CLASS_NAME, "player-info")
    table_length = len(player_elements)

    metadata = {
        "columns": columns,
        "table_length": table_length
    }

    return metadata


def collect_table_data(driver):
    """
    Collect text from all sub elements of table
    """
    table = driver.find_elements(By.CLASS_NAME, "Table__odd")

    table_data = []
    for row in table:
        try:
            table_data.append(row.text.split("\n"))
        except:
            table_data.append([])

    return table_data


def next_page(driver):
    """
    Find next page button, return false if we are on the last page, otherwise
    click the button and return true
    """
    button = driver.find_element(By.CLASS_NAME, "Pagination__Button--next")

    if button.get_attribute('aria-disabled') == "true":
        return False

    button.click()
    return True


def extract():
    """
    Execute data collection processes for 2021/2022 espn fantasy football data
    Data containing season level statistics for all players
    """
    driver = create_driver()
    navigate_to_scoring_leaders(driver)
    metadata = collect_table_metadata(driver)

    player_data = []
    next_page_exists = True
    while next_page_exists:
        player_data.append(collect_table_data(driver))
        next_page_exists = next_page(driver)
        
    return player_data, metadata


def transform(raw_data, metadata):
    """
    Data transformation from raw to structured
    """
    data_len = metadata['table_length']
    master_dataset = []

    # iterate over pages
    for page in raw_data:

        # collect all data associated with each player
        page_data = [[] for i in range(data_len)]
        for i, data_set in enumerate(page):
            for data in data_set:
                page_data[i % data_len].append(data)
        
        # remove empty data and health status
        for player in page_data:
            if len(player) == 0:
                continue
            if len(player) == 20:
                player.pop(1)
            master_dataset.append(player)

    return master_dataset


def etl():
    """
    Pipeline to facilitate extract, tranform, load
    """
    player_data, metadata = extract()
    clean_data = transform(player_data, metadata)

    return pd.DataFrame(clean_data, columns=metadata['columns'])
