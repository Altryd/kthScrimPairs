import csv
import json


def find_player(nickname: str, set_of_players_lower: set, list_of_players_json_sorted: list):
    if nickname.lower() not in set_of_players_lower:
        raise KeyError(f"Такого игрока не существует в json! Nickname: {nickname}")
    else:
        found_player = list(filter(lambda player: player["nickname"].lower() == nickname.lower(),
                                   list_of_players_json_sorted))[0]
        return found_player["nickname"]


def form_pairs(players: list, pairs_correction=None, csv_out=None):
    """

    :param players:
        list of dict. Needed keys:
            "nickname": str,
            "rating": int or float,
            "played_against": list, example:
                "played_against": [
                        {
                        "second_player_id": 0,
                        "first_player_score": "6",
                        "second_player_score": "4"
                        }
                    ]
            "discordId": str,
            "active": bool,
            "user_id": int
    :param pairs_correction:
        list of list with nicknames, ex: [["Vaxei", "mrekk"], ["Akolibed", "Chicony"]]
    :param csv_out:
        path to csv
    :return:
    """
    used_players = set()
    overpowered_players = set()
    players = list(filter(lambda player: player["active"], players))
    SET_OF_ALL_PLAYERS = set([player["nickname"] for player in players])
    SET_OF_ALL_PLAYERS_lower = set([player["nickname"].lower() for player in players])
    list_of_players_json_sorted = sorted(players, key=lambda player: player["rating"], reverse=True)
    pairs = []

    if pairs_correction:
        for pair_correction in pairs_correction:
            pair_correction[0] = find_player(pair_correction[0], SET_OF_ALL_PLAYERS_lower, list_of_players_json_sorted)
            pair_correction[1] = find_player(pair_correction[1], SET_OF_ALL_PLAYERS_lower, list_of_players_json_sorted)
            players_tuple = tuple(filter(lambda player:
                                  player["nickname"] == pair_correction[0]
                                  or player["nickname"] == pair_correction[1], list_of_players_json_sorted))
            # player = players_tuple[0]
            pairs.append(players_tuple)
            used_players.add(players_tuple[0]["nickname"])
            used_players.add(players_tuple[1]["nickname"])

    for player in list_of_players_json_sorted:
        if player["nickname"] in used_players:
            continue
        for player_second in list_of_players_json_sorted:
            if player_second["nickname"] in used_players or player_second["user_id"] == player["user_id"]:
                continue
            played_against_ids = [player_["second_player_id"] for player_ in player["played_against"]]
            if player_second["user_id"] in played_against_ids:
                continue
            if player["rating"] - player_second["rating"] >= 300:
                overpowered_players.add((player["nickname"], player['rating']))
                used_players.add(player["nickname"])
                # print("Cannot find a decent opponent because of rating for: {0}, rating {1}".format(player["nickname"], player["rating"]))
                print("Невозможно найти подходящего соперника из-за SKILL ISSUE рейтинга для: {0}, rating {1}".format(
                    player["nickname"],
                    player["rating"]))
                break
            pairs.append((player, player_second))
            used_players.add(player["nickname"])
            used_players.add(player_second["nickname"])
            break
    unused_list = list(SET_OF_ALL_PLAYERS.difference(used_players))
    for unused in unused_list:
        print(f"Неиспользованные игроки "
              f"(по другим причинам, скорее всего из-за нехватки еще одного игрока для формирования пары): "
              f"{unused}")
    print("\n")
    # overpowered_players = sorted(overpowered_players, key=lambda player: player[1], reverse=True)
    # print("overpowered players: ", overpowered_players)
    for pair in pairs:
        print(
            "{0} ({1}) vs {2} ({3})".format(pair[0]["nickname"], pair[0]["rating"], pair[1]["nickname"],
                                            pair[1]["rating"]))

    print("\nfor discord:")
    data = []
    for pair in pairs:
        print("<@{0}>\tvs\t<@{1}>".format(pair[0]["discordId"], pair[1]["discordId"]))
        data.append([pair[0]["nickname"], pair[1]["nickname"]])

    print("\n\n[DEBUG]")
    print(f"all_players_count: {len(SET_OF_ALL_PLAYERS)}")
    print(f"used_players_count (incl.rating issues): {len(used_players)}")
    print(f"unused players: {SET_OF_ALL_PLAYERS.difference(used_players)}")
    if csv_out:
        with open(f'{csv_out}', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            # write the data
            writer.writerows(data)
    return data


if __name__ == "__main__":
    with open(r"data_in/data_with_played.json", "r") as file:
        players = json.loads(file.read())
    form_pairs(players, pairs_correction=[["Suzuha", "Boriska"]])
