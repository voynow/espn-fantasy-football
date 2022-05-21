from locale import normalize
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


def get_player_links(driver):

    player_links = driver.find_elements(By.CLASS_NAME, "link")
    player_links[0].click()
    player_card = driver.find_element(By.CLASS_NAME, "player-card-center")
    # player_card = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "player-card-center")))
    # player_card = player_links[0].find_element(By.CLASS_NAME, "player-card-center")
    print(player_card.text)


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

    player_data = []
    next_page_exists = True
    while next_page_exists:
        get_player_links(driver)
        1/0
        # next_page_exists = next_page(driver)
        
    return player_data
