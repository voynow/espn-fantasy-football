import pickle

position_replace_subkey_mapping = {
    "QB": " PASSING RUSHING",
    "RB": " RUSHING RECEIVING FUMBLES",
    "WR": " RECEIVING RUSHING FUMBLES",
    "TE": " RECEIVING RUSHING FUMBLES",
}

dict_keys = {
    "info": ["team", "number", "position"],
    "postseason": ["date", "vs_#", "opponent", "outcome", "score", "stats", "game_title"],
    "2021regularseason": ["date", "vs_#", "opponent", "outcome", "score", "stats"]
}

position_stats_columns = {
    "QB": {
        "passing": ['CMP', 'ATT', 'YDS', 'CMP%', 'AVG', 'TD', 'INT', 'LNG', 'SACK', 'RTG', 'QBR'],
        "rushing": ['ATT', 'YDS', 'AVG', 'TD', 'LNG']
    },
    "RB": {
        "rushing": ['ATT', 'YDS', 'AVG', 'TD', 'LNG'],
        "receiving": ['REC', 'TGTS', 'YDS', 'AVG', 'TD', 'LNG'],
        "fumbles": [ 'FUM', 'LST', 'FF', 'KB']
    },
    "WR": {
        "receiving": ['REC', 'TGTS', 'YDS', 'AVG', 'TD', 'LNG'],
        "rushing": ['ATT', 'YDS', 'AVG', 'LNG', 'TD'],
        "fumbles": ['FUM', 'LST', 'FF', 'KB']
    },
    "TE": {
        "receiving": ['REC', 'TGTS', 'YDS', 'AVG', 'TD', 'LNG'],
        "rushing": ['ATT', 'YDS', 'AVG', 'LNG', 'TD'],
        "fumbles": ['FUM', 'LST', 'FF', 'KB']
    }
}


def load_to_dict(path_to_pkl):
    """
    Load pickle file, transform into dictionary where key=player_name, value=player_data
    """
    f = open(path_to_pkl, 'rb')
    load_data = pickle.load(f)
    data_list = [[table.split("\n") for table in player] for player in load_data]
    data_dict = {player[0][0]: player[1:] for player in data_list}

    return data_dict


def transform_tables(data):
    """
    Insert player's tables into dictionary format
    """
    for key, value in data.items():
        info = value[0]
        position = info[-1]
        data[key] = {"info": info}

        for table in value[1:]:
            subkey = table[0].replace(position_replace_subkey_mapping[position], "")
            subkey = subkey.replace(" ", "").lower()
            data[key][subkey] = table

    return data


def get_mod(key):
    """
    Modulo value for grouping data
    """
    if key == 'postseason':
        return 7
    if key == '2021regularseason':
        return 6
    else:
        raise ValueError(f"Table name invalid: {key}")


def extract_game_data(table):
    """
    Remove information - table dependent
    """
    last_entry = table[-1].split(" ")[0]
    game_data = table[5:]
    if last_entry == "POSTSEASON" or last_entry == "REGULAR":
        game_data = game_data[:-1]

    return game_data


def group_data_by_feature(game_data, mod):
    """
    Collecting features
    """
    game_groups = [[] for _ in range(mod)]
    for i, item in enumerate(game_data):
        game_groups[i % mod].append(item)
    
    return game_groups

def group_statistics(data_dict):
    """
    Add structure to game data - consolidation by feature
    """
    for player, data in data_dict.items():
        for key, table in data.items():
            if key != 'info':
                mod = get_mod(key)
                game_data = extract_game_data(table)
                game_groups = group_data_by_feature(game_data, mod)
                data_dict[player][key] = game_groups
    
    return data_dict


def transform_grouped_data(data_dict):
    """
    Add keys to group data - dictionary transformation
    """
    for player, data in data_dict.items():
        for key, table in data.items():
            data_dict[player][key] = {
                dict_keys[key][i]: item for i, item in enumerate(table)}
    return data_dict


def create_stats_dict(stats_list, columns):
    """
    Apply column name to game statistics
    """
    stats_dict = {}
    for stats in stats_list:
        stats = stats.split(" ")

        idx = 0
        for col_set, column_names in columns.items():
            for col in column_names:
                stat = stats[idx]
                key = f"{col_set}_{col}"
                if key not in stats_dict:
                    stats_dict[key] = []
                stats_dict[key].append(stat)
                idx += 1
        
    return stats_dict


def transform_game_stats(data_dict):
    """
    Structure game statistics with feature name
    """
    for player, data in data_dict.items():
        for key, table in data.items():
            if key == 'info':
                pos = table['position']
            if key == "postseason" or key == "2021regularseason":
                stats = create_stats_dict(table['stats'], position_stats_columns[pos])
                for stat_name, stat_value in stats.items():
                    data_dict[player][key][stat_name] = stat_value
                del data_dict[player][key]['stats']

    return data_dict

def transform():

    path_to_pkl = 'data/game_level.pkl'

    player_data_dict = load_to_dict(path_to_pkl)
    player_data_dict = transform_tables(player_data_dict)
    player_data_dict = group_statistics(player_data_dict)
    player_data_dict = transform_grouped_data(player_data_dict)
    player_data_dict = transform_game_stats(player_data_dict)

    return player_data_dict