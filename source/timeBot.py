import sys
import time
import json
import requests
import datetime
import threading
import config
from functions import epoch_to_time, time_to_epoch
from city import City


class TimeBot():
    def __init__(self) -> None:
        self.csrf_token = config.tokens["csrf_token"]
        self.h_token = config.tokens["h_token"]
        self.world = config.tokens["world"]
        self.cookies = {"sid": f"{self.csrf_token}"}
        self.headers = {"X-Requested-With": "XMLHttpRequest",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}

    def send_units(self, source_id, destination_id,  units, _type):
        """
            source_id: id/bbcode of city sending units
            destination_id: id/bbcode of city receiving units
            units: units to send
            _type: "support" | "attack"
        """
        print(f"Trying to send: {units} from {source_id} to {destination_id}")
        url = f"https://{self.world}.grepolis.com/game/town_info?action=send_units&h={self.h_token}"

        data = {"json": '{%s,"id":"%s","type":"%s","town_id":%s,"nl_init":true}' %
                (units, destination_id, _type, source_id)}

        r = requests.post(url, headers=self.headers,
                          cookies=self.cookies, data=data)

        return json.loads(r.text)

    def process_send_units_response(self, data, command_type="support"):
        notifs = data["json"]["notifications"]

        order = {}

        for x in notifs:
            if x["subject"] == "MovementsUnits" and x["param_str"].find(command_type):
                order = json.loads(x["param_str"])["MovementsUnits"]
                break

        # started_at gaan we kunnen gebruiken voor dodgen ((current_time - started at) * 2 -> wnr os terugkomt als we cancellen)
        started_at = order["started_at"]
        arrival_at = order["arrival_at"]
        command_id = order["command_id"]

        return arrival_at, command_id

    def cancel_command(self, id_to_cancel, source_town_id):
        print("Cancelling")
        url = f"https://{self.world}.grepolis.com/game/town_overviews?town_id={source_town_id}&action=cancel_command&h={self.h_token}"
        data = {"json": '{"id\":"%s\","town_id":%s,"nl_init":true}' %
                (id_to_cancel, source_town_id)}

        requests.post(url, headers=self.headers,
                      cookies=self.cookies, data=data)

    def calculate_difference(self, arrival_tijd, gewenste_arival, command_id, source_town_id, max_difference):
        difference = gewenste_arival - arrival_tijd
        print(
            f"[{difference}s] - Arrival: {epoch_to_time(arrival_tijd)} - desired arrival: {epoch_to_time(gewenste_arival)}")

        if difference <= max_difference and difference >= 0:
            return True

        elif difference <= -20:
            self.cancel_command(command_id, source_town_id)
            return False

        else:
            self.cancel_command(command_id, source_town_id)
            if difference - 5 < 20:
                print("Not close enough, trying again in 0.1 Seconds")
                time.sleep(0.1)
            else:
                print("Sleeping: ", difference - 20, "seconds")
                time.sleep(difference - 20)

    def time_bot(self, _type, source_id, destination_id, hour, minute, second, units, max_difference=2):
        i = 1
        while True:
            print("------ Attempt: ", i, "------")
            response_data = self.send_units(
                source_id, destination_id, units, _type)
            try:
                arrival_at, command_id = self.process_send_units_response(
                    response_data)
            except KeyError:
                print("Units aren't back yet - sleep 0.1 sec")
                time.sleep(0.1)  
                continue
            gewenste_arival = time_to_epoch(hour, minute, second)
            print(f"Desired Arrival: {epoch_to_time(gewenste_arival)}")
            arrival_at = int(arrival_at)
            resp_calc = self.calculate_difference(
                arrival_at, gewenste_arival, command_id, source_id, max_difference)
            i += 1

            if resp_calc == True or resp_calc == False:  # ! huh wtf is dit
                break



    def generate_units_str_to_send(self, units_dict, units_list: list = [], percentage=100):
        return_str = ""
        if len(units_list) == 0:
            if percentage != 100:
                for unit, amount in units_dict.items():
                    units_dict[unit] = int(amount * percentage / 100)
            
            for unit, amount in units_dict.items():
                return_str += f'"{unit}":{amount},'
            
            return return_str[:-1]

            
        else:
            units_to_send = {key: value for key,
                            value in units_dict.items() if key in units_list}

            if percentage != 100:
                for unit, amount in units_to_send.items():
                    units_to_send[unit] = int(amount * percentage / 100)

            for unit, amount in units_to_send.items():
                return_str += f'"{unit}":{amount},'

            return return_str[:-1]

    def main(self):
        city_1 = City(7610) # BBcode of your city
        units = city_1.get_all_units() # Getting available units

        print(units)

        # Generating units to send, give a list of units you want to send, in my case i only want to send slingers
        units_to_send = self.generate_units_str_to_send(units, ["slinger"]) 

        # support/attack                    #City to attack, #hour, minute, second desired arrival
        self.time_bot("support", city_1._id, 7613, 16, 21, 40, units_to_send, max_difference=1)
        # Set max difference to 0 if you want to only send units when they arrive at the exact time, otherwise it will cancel the command and try again
        # Understand that the lower the max difference, the more likely your units will never be sent
        # a max_difference of 3 should be successful 90% of the time


if __name__ == "__main__":
    timebot = TimeBot()
    timebot.main()
