from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time


def create_driver():
    """
    Create driver and load espn fantasy football page
    """
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://fantasy.espn.com/football/leaders")

    return driver


def get_player_links(driver):
    """
    Find link objects for all players on given page
    """
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "link")))
    player_links = driver.find_elements(By.CLASS_NAME, "link")

    return player_links


def access_player_card(driver, link):
    """
    Open player card and click on player's "complete stats"
    """
    player_name = link.text
    print(player_name)
    print(f"Link: {link}")
    link.click()
    try:
        player_card = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "player-card-center")))
        print(f"Player card: {player_card}")
    except:
        print(f"ERROR: skipping {player_name} - could not find class_name=player-card-center")
        return False
    player_card.find_element(By.CLASS_NAME, "header_link").click()
    return player_name


def switch_to_new_window(driver):
    """
    Update driver window to most recent window
    """
    new_window = driver.window_handles[-1]
    print(f"New window: {new_window}")
    if base_window is None:
        base_window = driver.window_handles[-2]
    print(f"Base window: {base_window}")
    driver.switch_to.window(new_window)

    return driver, base_window


def access_game_log(driver):
    """
    Within player statistics page -> click game log
    """
    nav_elements = driver.find_elements(By.CLASS_NAME, "Nav__Text")
    for element in nav_elements:
        if element.text == "Game Log":
            element.click()
            break
    time.sleep(.25)

    return driver


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


def switch_to_base_window(driver, base_window):
    """
    Update driver window to original window
    """
    driver.close()
    driver.switch_to.window(base_window)

    return driver


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
    player_links = get_player_links(driver)

    base_window = None
    data_collection = []
    for link in player_links:
        
        player_name = access_player_card(driver, link)
        if not player_name:
            continue

        driver, base_window = switch_to_new_window(driver)
        driver = access_game_log(driver)
        player_data = collect_data(driver, player_name)
        data_collection.append(player_data)
        driver = switch_to_base_window(driver, base_window)
        driver.find_element(By.CLASS_NAME, "lightbox__closebtn").click()

    return data_collection


    # player_data = []
    # next_page_exists = True
    # while next_page_exists:
    #     player_data.append(get_player_links(driver))
    #     next_page_exists = next_page(driver)
        
    # return player_data