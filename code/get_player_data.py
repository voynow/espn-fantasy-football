from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

import time
import numpy as np
import pandas as pd


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
    nav = driver.find_element(By.CLASS_NAME, 'global-nav-container')
    sub_navs = nav.find_elements(By.CLASS_NAME, 'sub')

    for item in sub_navs:
        nav_link = item.find_element(By.CLASS_NAME, 'link-text')
        if nav_link.text == 'Scoring Leaders':
            nav_link.click()
            time.sleep(5)
            break

def collect_scoring_leaders_data(driver):

    # find correct dropdowns
    dropdown_items = driver.find_elements(By.CLASS_NAME, "dropdown__select")
    for item in dropdown_items:
        if "NFL Week" in item.text:
            select = Select(item)
            dropdown_items = item.text.split("\n")[3:]

            # iterate over all weeks
            # excluding first two dropdowns and possibly current week
            week_dfs = []
            week_idxs = []
            colnames = ""
            get_colnames = True
            for dropdown in dropdown_items:
                select.select_by_visible_text(dropdown)
                tables = driver.find_elements(By.CLASS_NAME, "Table")

                # iterate over first 20 pages
                week_data = []
                for i in range(2):

                    # iterate over all tables in page
                    for j, table in enumerate(tables):
                        if get_colnames:
                            colnames += table.find_element(
                                By.CLASS_NAME, "Table__sub-header").text + "\n"
                        rows = table.find_element(By.CLASS_NAME, "Table__TBODY").find_elements(
                            By.CLASS_NAME, 'Table__TR')

                        # edge case for first table (remove injury indicator)
                        if not j:
                            table_data = []
                            for row in rows:
                                row_list = row.text.split("\n")
                                if row_list[1] in ['D', 'O', 'Q', 'IR']:
                                    row_list.remove(row_list[1])
                                table_data.append(row_list)

                        # create concatenate new rows onto table_data, axis=1
                        else:
                            table_data = [
                                table_row + row.text.split("\n") for table_row, row in zip(table_data, rows)]

                    # turn off find elements colnames and save data
                    if get_colnames:
                        colnames = colnames.split("\n")[:-1]
                    get_colnames = False
                    week_data.append(pd.DataFrame(table_data, columns=colnames))

                    # go to next page
                    driver.find_element(
                        By.CLASS_NAME, "Pagination__Button--next").click()

                # collect data
                week_dfs.append(pd.concat(week_data))
                week_idxs.append(int(dropdown[-1]))

    return week_dfs


def main():

    # open espn
    driver = create_driver()

    # select scoring leaders tab
    navigate_to_scoring_leaders(driver)

    # collect all player data over all weeks
    week_dfs = collect_scoring_leaders_data(driver)

    # close web driver
    driver.close()

    # encode week number
    week_dfs = week_dfs[::-1]
    for i in range(len(week_dfs)):
        week_dfs[i]["week"] = i + 1

    # concat data, remove players who score 0 points
    df = pd.concat(week_dfs)

    # Remove Bye week data, FA players, and players with no fpts score
    df = df[df["OPP"] != "*BYE*"]
    df = df[df["OPP"] != "--"]
    df = df[df['FPTS'] != "--"]

    # Remove @, fix 0 data, make dtype float
    df['OPP'] = df['OPP'].apply(lambda x: x.replace('@', ''))
    df['FPTS'] = df['FPTS'].astype('float')

    # reset index
    df.reset_index(inplace=True, drop=True)

    # save data
    df.to_csv("data/player_data.csv")

main()
