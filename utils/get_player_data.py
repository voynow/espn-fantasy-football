from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import time


def create_driver():
    """
    create driver and load espn fantasy football page
    """
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://fantasy.espn.com/football")

    return driver


def navigate_to_scoring_leaders(driver):
    """
    """
    navs = driver.find_element(By.CLASS_NAME, 'global-nav-container').find_elements(By.CLASS_NAME, 'sub')

    for item in navs:
        nav_link = item.find_element(By.CLASS_NAME, 'link-text')
        if nav_link.text == 'Scoring Leaders':
            nav_link.click()
            time.sleep(5)
            break

def collect_table_metadata(driver):

    # get column names
    header_elements = driver.find_elements(By.CLASS_NAME, "header")
    columns = [element.text for element in header_elements]

    # find num players in table
    player_elements = driver.find_elements(By.CLASS_NAME, "player-info")
    table_length = len(player_elements)

    # collect data in dictionary
    metadata = {
        "columns": columns,
        "table_length": table_length
    }

    return metadata


def collect_table_data(driver):

    # access data from table containing player data
    table = driver.find_elements(By.CLASS_NAME, "Table__odd")

    table_data = []
    for row in table:
        try:
            table_data.append(row.text.split("\n"))
        except:
            table_data.append([])

    return table_data


def next_page(driver):

    button = driver.find_element(By.CLASS_NAME, "Pagination__Button--next")

    if button.get_attribute('aria-disabled') == "true":
        return False

    button.click()
    return True


def exe():

    # navigate to espn ff scoring leaders page
    driver = create_driver()
    navigate_to_scoring_leaders(driver)

    # get columns and table length
    metadata = collect_table_metadata(driver)

    player_data = []
    next_page_exists = True
    while next_page_exists:
        player_data.append(collect_table_data(driver))
        next_page_exists = next_page(driver)
        
    return player_data, metadata