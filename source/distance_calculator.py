"""
Never really used it, but can be useful so didn't delete it.
"""
from datetime import datetime
import requests
import math
from config import tokens
from timeBot import epoch_to_time, time_to_epoch

h_token = tokens.get("h_token")
csrf_token = tokens.get("csrf_token")
world = tokens.get("world")

MYTHICAL_UNITS = {"cerberus": 16, "erinyes": 40, "minotaur": 40, "manticore": 88,
                  "cyclops": 32, "hydra": 32, "harp": 42, "medusa": 24, "centaur": 12, "pegasus": 140,
                  "griff": 72, "fat ass pig": 64, "sirene": 88, "sater": 544, "spartoi": 64, "ladon": 160}

LAND_UNITS = {'sword': 32, 'slinger': 56, 'archer': 48, 'hoplite': 24, 'rider': 88, 'chariot': 72, 'catapult': 8,
              'godsent': 64}

SEA_UNITS = {'big_transporter': 32, 'bireme': 60, 'attack_ship': 52,
             'small_transporter': 60, 'trireme': 60, 'colonize_ship': 12}

ALL_UNITS = {**LAND_UNITS, **SEA_UNITS}


cookies = {"sid": f"{csrf_token}"}
headers = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
}


def sent_runtime_request(from_town, to_town):
    url = f"https://{world}.grepolis.com:443/game/town_info"
    params = {
        'town_id': str(from_town),
        'action': 'support',
        'h': h_token,
        'json': '{"id":%s,"town_id":%s,"nl_init":true}' % (to_town, from_town),
    }

    r = requests.get(url, headers=headers,
                     cookies=cookies, params=params).json()
    return r




def proccess_response(json_data):
    json_data = json_data["json"]
    json_data = json_data["json"]

    distance = json_data["units"]["sword"]["distance"]
    print("Distance: " + str(distance))
    print("---------------SEA-------------")
    for unit in ALL_UNITS:
        duration = arrival_time_calulator(distance, ALL_UNITS[unit])
        duration_in_readable = seconds_to_time(int(duration))
        print(
            f"{unit}, Duration: {duration} - {duration_in_readable}")




def arrival_time_calulator(distance, unit_speed):
    """FORMULE: 
    (distance x 50) / unit_speed + tijdwereld(5min voor wereld snelheid3, 15min voor snelheid 1)
    """
    speciale_shit = {"cartografie": 0.90, "zeilen_plaatsen": 0.90, "verbeterde_troepenbeweging": 0.70, "vuurtoren": 0.85,
                     "atalanta": {
                         "level1": 0.89,
                         "level2": 0.88,
                         "level3": 0.87,
                         "level4": 0.86,
                         "level5": 0.85,
                         "level6": 0.84,
                         "level7": 0.83,
                         "level8": 0.82,
                         "level9": 0.81,
                         "level10": 0.80,
                         "level11": 0.79,
                         "level12": 0.78,
                         "level13": 0.77,
                         "level14": 0.76,
                         "level15": 0.75,
                         "level16": 0.74,
                         "level17": 0.73,
                         "level18": 0.72,
                         "level19": 0.71,
                         "level20": 0.70
                     }}

    return math.floor((distance * 50) / unit_speed + 300)


def seconds_to_time(seconds):
    now = datetime.now()
    full_hours = math.floor(seconds/3600)
    rest = (seconds / 3600) % 1
    minutes = math.floor(rest * 60)
    seconds = round((rest * 60) % 1, 2) * 60

    return f"{full_hours}:{minutes}:{round(seconds, 2)}"


def main():
    arrival_time_calulator(100, 24)
    r = sent_runtime_request(7707, 5937)
    proccess_response(r)


if __name__ == "__main__":
    main()
