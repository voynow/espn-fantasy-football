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


def get_player_links(driver):

    player_links = driver.find_elements(By.CLASS_NAME, "link")

    base_window = None
    data_collection = []
    for link in player_links:
        print(link.text)
        print(f"Link: {link}")
        link.click()
        try:
            player_card = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "player-card-center")))
            print(f"Player card: {player_card}")
        except:
            print(f"ERROR: skipping {link.text} - could not find class_name=player-card-center")
            continue
        player_card.find_element(By.CLASS_NAME, "header_link").click()

        new_window = driver.window_handles[-1]
        print(f"New window: {new_window}")
        if base_window is None:
            base_window = driver.window_handles[-2]
        print(f"Base window: {base_window}")
        driver.switch_to.window(new_window)

        nav_elements = driver.find_elements(By.CLASS_NAME, "Nav__Text")
        for element in nav_elements:
            if element.text == "Game Log":
                element.click()
                break
        time.sleep(1)

        player_data_2021 = []
        data_tables = driver.find_elements(By.CLASS_NAME, "mb4")
        print("Found the following data tables:")
        for i, table in enumerate(data_tables):
            print(f"{i} {table}")
            player_data_2021.append(table.text)
        data_collection.append(player_data_2021)

        driver.close()
        driver.switch_to.window(base_window)
        driver.find_element(By.CLASS_NAME, "lightbox__closebtn").click()
        print("\n")

    return data_collection


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

    # player_data = []
    # next_page_exists = True
    # while next_page_exists:
    #     player_data.append(get_player_links(driver))
    #     next_page_exists = next_page(driver)
        
    # return player_data

    return get_player_links(driver)
