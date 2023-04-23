import time
import random
from city import City
from config import tokens
from command_checker import CommandOverview
from goldbot import GoldBot
import threading


class GrepoBot():
    def __init__(self, cities):
        self.cities = cities
        self.username = tokens.get("username")
        self.password = tokens.get("password")
        self.csrf_token = tokens.get("csrf_token")
        self.h_token = tokens.get("h_token")
        self.world = tokens.get("world")
        self.command_checker = CommandOverview(self.cities[0]._id)
        self.gold_bot = GoldBot(self.cities[0]._id)

    def get_all_land_units(self):
        all_units_dict = {}
        for city in self.cities:
            for key, value in city.get_all_land_units()["all_units"].items():
                if(key not in all_units_dict):
                    all_units_dict[key] = value
                else:
                    all_units_dict[key] += value

        return all_units_dict

    def get_all_player_land_units(self):
        """ 
        Returns a dictionarry of ALL units the current user owns(doesnt include support). 
        """
        all_units_dict = {}
        for city in self.cities:
            for key, value in city.get_land_units()["player_units"].items():
                if(key not in all_units_dict):
                    all_units_dict[key] = value
                else:
                    all_units_dict[key] += value

        return all_units_dict

    def get_all_player_land_support_units(self):
        """ 
        Returns a dictionarry of ALL units the current user owns(doesnt include support). 
        """
        return dict(set(self.get_all_land_units().items() - set(self.get_all_player_land_units().items())))

    def upgrade_buildings_all_cities(self):
        while True:
            for city in self.cities:
                city.upgrade_buildings()
            time.sleep(3600) 


    def farm_all_villages_cities(self, option=1):
        while True:
            for city in self.cities:
                city.farm_all_villages(option)
            time.sleep(random.randint(600, 650))

    def check_commands(self):
        self.command_checker.main()

    def run_gold_bot(self):
        self.gold_bot.run_bot()


    def main(self):
        command_thread = threading.Thread(target=self.check_commands, daemon=True)
        farm_thread = threading.Thread(target=self.farm_all_villages_cities,
                         daemon=True)
        build_thread = threading.Thread(target=self.upgrade_buildings_all_cities, daemon=True)
        gold_bot_thread = threading.Thread(target=self.run_gold_bot, daemon=True)

        build_thread.start()
        command_thread.start()
        farm_thread.start()
        gold_bot_thread.start()

        while True:
            print(f"Command_thread status: {command_thread.is_alive()}")
            print(f"Farm_thread status: {farm_thread.is_alive()}")
            print(f"Build_thread status: {build_thread.is_alive()}")
            print(f"Gold_bot_thread status: {gold_bot_thread.is_alive()}")
            time.sleep(60)



