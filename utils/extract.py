from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException

import json


def create_driver(link):
    """
    Create chrome driver given web link
    """
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(link)

    return driver

def wait_for_element(driver, by, html, wait_duration=5):
    """
    find element with web driver wait, defult 5 seconds
    """
    condition = EC.presence_of_element_located((by, html))
    element = WebDriverWait(driver, wait_duration).until(condition)

    return element


def get_first_player(driver):
    """
    Find link object for first player on given page
    """
    wait_for_element(driver, By.CLASS_NAME, "Table__TBODY", wait_duration=15)
    player_links = driver.find_elements(By.CLASS_NAME, "link ")
    clean_player_links = [player_link for player_link in player_links if player_link.text]
    first_player = clean_player_links[0]

    return first_player


def collect_data(driver, player_name):
    """
    Collect text returned from all table elements
    """
    game_level_data = [player_name]
    data_tables = driver.find_elements(By.CLASS_NAME, "mb4")
    for i, table in enumerate(data_tables):
        print(f"{i} {table}")
        game_level_data.append(table.text)
    return game_level_data


def get_link_map(web_link):
    """
    
    """
    driver = create_driver(web_link)
    get_first_player(driver).click()
    wait_for_element(driver, By.CLASS_NAME, "player-card-center")
    
    player_link_map = {}
    next_player_exists = True
    while next_player_exists:
        player_name_element = driver.find_element(By.CLASS_NAME, "player-name")
        player_name = player_name_element.text.replace("\n", " ")

        complete_stats_obj = driver.find_element(By.CLASS_NAME, "header_link")
        link_stats = complete_stats_obj.get_attribute('href')
        link_gamelog = link_stats.replace("stats", "gamelog")
        player_link_map[player_name] = link_gamelog
        
        try:
            next_player = driver.find_element(By.CLASS_NAME, "right-box")
            next_player.click()
        except ElementNotInteractableException:
            next_player_exists = False 

    return player_link_map


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


def extract(create_new_link_map=False):
    """

    """
    espn_ff_scoring_laders_link = "https://fantasy.espn.com/football/leaders"
    player_link_map_loc = 'data/json/player_link_map.json'

    if create_new_link_map:
        player_link_map = get_link_map(espn_ff_scoring_laders_link)

        with open(player_link_map_loc, "w") as f:
            json.dump(player_link_map, f, indent=4)
    else:
        with open(player_link_map_loc) as f:
            player_link_map = json.load(f)

    data_collection = []
    for player_name, link in player_link_map.items():

        if link:
            player_driver = create_driver(link)
            player_data = collect_data(player_driver, player_name)
            data_collection.append(player_data)
            player_driver.quit()

    return data_collection


    # player_data = []
    # next_page_exists = True
    # while next_page_exists:
    #     player_data.append(get_player_links(driver))
    #     next_page_exists = next_page(driver)
        
    # return player_data