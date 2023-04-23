import requests
import time
from datetime import datetime
from dhooks import Webhook
from config import tokens
from city import City
from functions import epoch_to_time, time_to_epoch
hook = Webhook(tokens.get("discord_hook"))

from city import City
from timeBot import TimeBot
import threading

class CommandOverview():
    def __init__(self, town_id) -> None:
        self.town_id = town_id
        self.attack_types = ['attack', 'attack_land', 'attack_sea',
                             'attack_takeover', 'illusion', 'portal_attack_olympus', 'revolt']
        self.h_token = tokens.get("h_token")
        self.csrf_token = tokens.get("csrf_token")
        self.world = tokens.get("world")
        self.headers = {
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        }
        self.cookies = {"sid": f"{self.csrf_token}"}
        self.already_seen = []

    def get_commands(self):
        url = f"https://{self.world}.grepolis.com/game/town_overviews?town_id={self.town_id}&action=command_overview&h={self.h_token}"

        r = requests.get(url, headers=self.headers,  cookies=self.cookies)
        return r.json()["json"]["data"]["commands"]
    

    def get_attack_commands(self):
        commands = self.get_commands()
        attack_commands = []
        for command in commands:
            if command["type"] == "attack":
                attack_commands.append(command)
        return attack_commands

    def find_total_vs(self, town_id):
        city = City(town_id)
        attack_ships = city.get_all_units()["attack_ships"]
        return attack_ships

    def oproepen_militie(self, town_id):
        url = f"https://{self.world}.grepolis.com/game/building_farm?town_id={town_id}&action=request_militia&h={self.h_token}"

        r = requests.post(url, headers=self.headers,
                          cookies=self.cookies)
        print(r.text)

    def dodge_attack(self, city_getting_attacked, destination_town_id, when_to_dodge):
        '''
        If you want to automatically dodge an attack, you can use this function, just uncomment it in the process_commands function.
        '''

        print(f"[ATTACK DODGER] [{city_getting_attacked}] -> Militie oroepen...")
        self.oproepen_militie(city_getting_attacked)

        city = City(city_getting_attacked)
        sea_units = city.get_all_sea_units()
        lands_units = city.get_all_land_units()

        sea_units = TimeBot().generate_units_str_to_send(sea_units)
        lands_units = TimeBot().generate_units_str_to_send(lands_units)


        while True:
            print(f"[ATTACK DODGER] [{city_getting_attacked}] -> Attack is coming in {round(when_to_dodge - datetime.now().timestamp(), 2)} seconds, sending units away when it's 20 seconds before arrival ")
            if datetime.now().timestamp() > when_to_dodge - 300:
                destination_town_id = City.get_random_town_from_island(city, city_getting_attacked)
                print(f"[ATTACK DODGER] [{city_getting_attacked}] Sending units to {destination_town_id} to dodge attack")
                resp = TimeBot().send_units(city_getting_attacked, destination_town_id, lands_units, _type="support")
                arrival_at, command_id_land = TimeBot().process_send_units_response(resp)
                
                time.sleep(20)
                TimeBot().cancel_command(command_id_land, city_getting_attacked)
                print(f"[ATTACK DODGER] [{city_getting_attacked}] -> Cancelled support to {destination_town_id} Successfully Dodged Attack")
                break
            else:
                time.sleep(1)


    def process_commands(self, command_list):
        if len(command_list) == 0:
            current_time = datetime.now().strftime('%H:%M:%S')
            output = f'[{current_time}] [TOWN {self.town_id}] [CommandChecker] -> No Commands'
            print(output)
            return
        
        for command in command_list:
            if command["id"] not in self.already_seen:
                self.already_seen.append(command["id"])
                command_type = command['type']
                if command_type == "attack":
                    self.already_seen.append(command["id"])
                    origin_town_id = command["origin_town_id"]
                    destination_town_id = command["destination_town_id"]

                    origin_town_player_name = command["origin_town_player_name"]
                    origin_town_name = command["origin_town_name"]
                    destination_town_name = command["destination_town_name"]

                    arrival_at = command["arrival_at"]

                    output = f"[{datetime.now().strftime('%H:%M:%S')}] [CommandChecker] -> [{command_type}]: {origin_town_player_name}, {origin_town_name} <--> {destination_town_name}(arrival: {epoch_to_time(arrival_at)})"
                    hook.send(output)
                    print(output)

                    # print("Dodge the attack...")
                    # thread = threading.Thread(target=self.dodge_attack, args=(destination_town_id, origin_town_id, arrival_at))
                    # thread.start()


            else:
                output = f"[{datetime.now().strftime('%H:%M:%S')}] [TOWN {self.town_id}] [CommandChecker] -> No new Commands"
                print(output)

    def main(self):
        while True:
            commands = self.get_commands()
            self.process_commands(commands)
            time.sleep(5)


def main():
    command_overview = CommandOverview(4970)
    command_overview.main()


if __name__ == "__main__":
    main()
