from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time


def create_driver(link):
    """
    Create chrome driver given web link
    """
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(link)

    return driver


def get_players(driver):
    """
    Find link objects for all players on given page
    """
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "link")))
    player_links = driver.find_elements(By.CLASS_NAME, "link")

    return player_links


def get_player_metadata(driver, link):
    """
    Open player card and click on player's "complete stats"
    """
    print(f"Link: {link}")
    player_name = link.text
    print(f"player_name: {player_name}")
    link.click()

    try:
        player_card = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "player-card-center")))
        print(f"Player card: {player_card}")
    except BaseException as e:
        print(e)
        print(f"ERROR cannot find {player_name}'s player card")
        return player_name, None

    complete_stats_obj = player_card.find_element(By.CLASS_NAME, "header_link")
    complete_stats_link = complete_stats_obj.get_attribute('href')

    return player_name, complete_stats_link


def collect_data(driver, player_name):
    """
    Collect text returned from all table elements
    """
    game_level_data = [player_name]
    data_tables = driver.find_elements(By.CLASS_NAME, "mb4")
    print("Found the following data tables:")
    for i, table in enumerate(data_tables):
        print(f"{i} {table}")
        game_level_data.append(table.text)
    return game_level_data


def get_links_player_stats(driver, players):
    """
    
    """
    player_link_map = {}
    for player in players:
        
        player_name, link = get_player_metadata(driver, player)
        if link:
            link = link.replace("stats", "gamelog")
        player_link_map[player_name] = link
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "lightbox__closebtn"))).click()
        except WebDriverException:
            driver.refresh()

    # remove irregular data
    player_link_map = {k: v for k, v in player_link_map.items() if k}

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


def extract():
    """

    """
    espn_ff_scoring_laders_link = "https://fantasy.espn.com/football/leaders"
    driver = create_driver(espn_ff_scoring_laders_link)
    players = get_players(driver)
    player_link_map = get_links_player_stats(driver, players)

    missing_players = []
    data_collection = []
    for player_name, link in player_link_map.items():

        if link:
            player_driver = create_driver(link)
            player_data = collect_data(player_driver, player_name)
            data_collection.append(player_data)
            player_driver.quit()
        else:
            missing_players.append(player_name)

    return data_collection, missing_players


    # player_data = []
    # next_page_exists = True
    # while next_page_exists:
    #     player_data.append(get_player_links(driver))
    #     next_page_exists = next_page(driver)
        
    # return player_data