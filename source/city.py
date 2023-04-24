import requests
import json
from datetime import datetime
import re
from termcolor import colored
import colorama
import random
from config import tokens
colorama.init()



class City():
    def __init__(self, town_id: int, farms=[], town_type="default"):
        self.town_id = town_id
        self.buildings = ["storage", "farm", "main",
                          "market", "docks", "barracks", "academy", "temple", "hide", "lumber", "stoner", "ironer", ]
        self.recruit = {"sea_units": ["big_transporter", "bireme", "attack_ship", "demolition_ship", "small_transporter",
                                      "trireme", "colonize_ship"], "land_units": ["sword", "slinger", "archer", "hoplite", "rider", "chariot", "catapult"]}
        self.world, self.csrf_token, self.h_token = tokens[
            "world"], tokens["csrf_token"], tokens["h_token"]
        self.all_units = {}
        self.sea_units = {}
        self.land_units = {}
        self.headers = {
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        }
        self.cookies = {"sid": f"{self.csrf_token}"}
        self.town_type = town_type

        self.farms = self.get_farm_villages()
        self.set_recruit_and_build_according_to_type()

    @property
    def _id(self) -> int:
        return self.town_id

    def set_recruit_and_build_according_to_type(self) -> None:
        """
        type steden: "vs", "bir", "def_lt", "off_lt"
        als het vs is moeten we zorgen dat we de juiste units recruiten en de juiste buildings upgraden, 
        zelfde voor alle andere types
        Dus de volgorde van self.buildings aanpassen en nog extra functies schrijven
        """
        if self.town_type == "vs":
            self.buildings = ["main", "farm", "storage", "docks",
                              "academy", "lumber", "ironer", "stoner", "temple"]
            self.recruit["sea_units"] = ["attack_ship"]

        elif self.town_type == "bir":
            self.buildings = ["main", "farm", "storage", "docks",
                              "academy", "lumber", "stoner", "ironer", "temple", "hide"]
            self.recruit["sea_units"] = ["bireme"]

        elif self.town_type == "def_lt":
            self.buildings = ["main", "farm", "storage", "barracks",
                              "academy", "lumber", "stoner", "ironer", "temple"]
            self.recruit["land_units"] = ["sword", "archer", "hoplite"]
            self.recruit["sea_units"] = ["big_transporter"]

        elif self.town_type == "off_lt":
            self.buildings = ["main", "farm", "storage", "barracks",
                              "academy", "lumber", "stoner", "ironer", "temple"]
            self.recruit["land_units"] = ["slinger", "rider", "hoplite"]
            self.recruit["sea_units"] = ["big_transporter"]

    def get_farm_villages(self) -> list[int]:
        """
        Returns the IDs of all villages on the island of the current city
        """
        farm_towns = []
        island_id = self.get_island()
        url = f"https://{self.world}.grepolis.com/game/island_info?town_id={self.town_id}&action=index&h={self.h_token}"
        params = {
            'json': '{"island_id": %d,"town_id":%d}' % (island_id, self.town_id)
        }
        data = requests.get(url, params=params, headers=self.headers,
                            cookies=self.cookies).json()["json"]["json"]
        farm_town_list = data["farm_town_list"]
        farm_towns = [int(farm_town["id"]) for farm_town in farm_town_list if farm_town["rel"] >= 1]
        self.farms = farm_towns
        return farm_towns
    
    def get_random_town_from_island(self, town_id) -> int:
        """
        Returns town_id of a random town on the island of the current city, to use for dodging
        """
        island_id = self.get_island()
        url = f"https://{self.world}.grepolis.com/game/island_info?town_id={town_id}&action=index&h={self.h_token}"
        params = {
            'json': '{"island_id": %d,"town_id":%d}' % (island_id, town_id)
        }
        data = requests.get(url, params=params, headers=self.headers,
                            cookies=self.cookies).json()
        
        if data["json"].get("error") is not None:
            raise Exception(data["json"]["error"])

        
        towns = data["json"]["json"]["town_list"]
        
        return random.choice(towns)["id"]

    def get_island(self) -> int:
        """
        Returns the island ID of the current city
        """
        url = f'https://{self.world}.grepolis.com/game/town_info'

        params = {
            'town_id': self.town_id,
            'action': 'info',
            'h': self.h_token,
            'json': '{"id": %s,"town_id":%s} ' % (self.town_id, self.town_id),
        }


        data = requests.get(url, headers=self.headers,
                            cookies=self.cookies, params=params).json()
        
        if data["json"].get("error") is not None:
            raise Exception(data["json"]["error"])
                
        island_id = int(data["plain"]["html"].split("gp_island_link")[1].split("<")[0].split(" ")[1])        
        self.island_id = island_id
        return island_id

    def get_buildings(self) -> dict:
        """
        Returns a dictionnary containing all special_buildings and normal_buildings and whether the queue is full.
        """
        return_dict = {
            "special_buildings": {},
            "normal_buildings": {},
            "queue_full": False
        }
        url = f"https://{self.world}.grepolis.com/game/building_main?town_id={self.town_id}&action=index&h={self.h_token}&json=%7B%22town_id%22%3A{self.town_id}%2C%22"

        json_data = requests.get(url, headers=self.headers,
                                 cookies=self.cookies).json()["json"]

        html = json_data["html"]

        # Kinda cursed, but it works
        html = html[html.find("group, ")+7:]
        html = html.replace('}}}, {"tower', '}}, "tower')
        special_buildings_json = json.loads(html[:html.find(");")])

        normal_buildings_html = html[html.find(
            " BuildingMain.buildings = ")+len(" BuildingMain.buildings = "):]
        end = normal_buildings_html.find("BuildingMain.full")
        buildings = normal_buildings_html[:end-6]
        normal_buildings_json = json.loads(buildings)

        is_queue_full = normal_buildings_html[end:end +
                                              50].split(" ")[2].rstrip(";\n")

        return_dict["special_buildings"] = special_buildings_json
        return_dict["normal_buildings"] = normal_buildings_json
        return_dict["queue_full"] = is_queue_full

        return return_dict

    
    def farm_village(self, village_id, option=1) -> None:
        """ 
        Getting the resources from one village (option 1-4) where 1 is a 5/10 minutes collection(aka first option) and 4 is the longest aka last option.
        Default: 1.
        """

        if option not in range(1, 5):
            raise Exception("Option has to be in range 1 - 4")

        url = f"https://{self.world}.grepolis.com/game/frontend_bridge?town_id={self.town_id}&action=execute&h={self.h_token}"

        data = {
            "json": '{"model_url":"FarmTownPlayerRelation/%s","action_name":"claim","arguments":{"farm_town_id":%s,"type":"resources","option":%s},"town_id":%s}' % (str(village_id), str(village_id), str(option), str(self.town_id))
        }

        r = requests.post(url, headers=self.headers,
                          data=data, cookies=self.cookies)

        json_data = json.loads(r.text)
        current_time = datetime.now().strftime("%H:%M:%S")

        try:
            output = f'[{current_time}] [TOWN {self.town_id}] [FarmBot] -> {village_id}:{json_data["json"]["success"]}'
            print(colored(output, "green"))
        except KeyError:
            output = f'[{current_time}] [TOWN {self.town_id}] [FarmBot] -> {village_id}:{json_data["json"]["error"]}'
            print(colored(output, "red"))

    def farm_all_villages(self, option=1):
        """
        To farm all villages belonging to that city.
        """
        [self.farm_village(village_id, option) for village_id in self.farms]

    def get_all_units(self) -> dict:
        """
        Returns a dictionary containing all units in the city where the key is the unit and the value the amount of units.
        """
        url = f"https://{self.world}.grepolis.com/game/building_place?town_id={self.town_id}&action=index&h={self.h_token}"

        r = requests.get(url, headers=self.headers,
                         cookies=self.cookies)
        json_data = json.loads(r.text)

        return json_data["json"]["data"]["player_units"]

    def get_all_land_units(self) -> dict:
        """ Get all land units in this city """
        land_units = ["sword", "slinger", "archer",
                      "hoplite", "rider", "chariot", "catapult"]
        land_units_dict = self.get_all_units()
        return_dict = {}
        for k, v in land_units_dict.items():
            if(k in land_units):
                return_dict[k] = v

        self.land_units = return_dict

        return return_dict

    def get_all_sea_units(self) -> dict:
        """ Get all sea units in this city """
        sea_units = ["big_transporter", "bireme", "attack_ship",
                     "demolition_ship", "small_transporter", "trireme", "colonize_ship"]
        sea_units_dict = self.get_all_units()
        return_dict = {}
        for k, v in sea_units_dict.items():
            if(k in sea_units):
                return_dict[k] = v

        self.sea_units = return_dict

        return return_dict

    def upgrade_building(self, building):
        """ Upgrade a building """
        url = f"https://{self.world}.grepolis.com/game/frontend_bridge?town_id={self.town_id}&action=execute&h={self.h_token}"
        data = {
            'json': '{"model_url":"BuildingOrder","action_name":"buildUp","arguments":{"building_id":"%s"},"town_id":%s}' % (building, self.town_id)
        }

        response = requests.post(
            url, headers=self.headers, data=data, cookies=self.cookies)
        return response.text

    def send_units(self, destination_id,  units, _type):
        """
            source_id: id/bbcode of city sending units
            destination_id: id/bbcode of city receiving units
            units: units to send
            _type: "support" | "attack"
        """
        print(
            f"Trying to send: {units} from {self.town_id} to {destination_id}")
        url = f"https://{self.world}.grepolis.com/game/town_info?town_ids={self.town_id}&action=send_units&h={self.h_token}"

        data = {"json": '{%s,"id":"%s","type":"%s","town_id":%s}' %
                (units, destination_id, _type, self.town_id)}

        r = requests.post(url, headers=self.headers,
                          cookies=self.cookies, data=data)

        return json.loads(r.text)

    def recruit_land_units(self) -> None:
        """Recruit land units in the city according to the city type"""
        pass

    def recruit_sea_units(self) -> None:
        """Recruit sea units in the city according to the city type"""
        pass

    def upgrade_buildings(self) -> None:
        """ Upgrade buildings in the city  """
        for building in self.buildings:
            r = json.loads(self.upgrade_building(building))
            current_time = datetime.now().strftime("%H:%M:%S")

            try:
                if r["json"]["error"]:
                    output = f"[{current_time}] [TOWN {self.town_id}] [CityBuilder] -> {r['json']['error']}"
                    print(colored(output, "red"))

            except KeyError:
                output = f"[{current_time}] [TOWN {self.town_id}] [{self.town_type}] [CityBuilder] -> Succesfully upgraded {building}"
                print(colored(output, "green"))


if __name__ == "__main__":
    city = City(11357)
    print(city.farm_all_villages())
