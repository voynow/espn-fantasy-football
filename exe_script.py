from code import get_player_data

# navigate to espn ff scoring leaders page
driver = get_player_data.create_driver()
get_player_data.navigate_to_scoring_leaders(driver)

# get columns and table length
metadata = get_player_data.collect_table_metadata(driver)

# collect data from current table
# iterate to next page if exists
# while True:
    # get_player_data.collect_table_data(driver)
    # try:
    #     # TODO create this function
    #     # get_player_data.next_page(driver)
    # except:
    #     break
