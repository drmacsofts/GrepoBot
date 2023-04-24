import requests
import sys
import time
import os
import json
import requests
from dhooks import Webhook
import random
import threading
import config
from config import tokens

hook = Webhook(tokens.get("discord_hook"))


class GoldBot:
    def __init__(self, bb_code_town):
        self.H_TOKEN = tokens.get("h_token")
        self.CSRF_TOKEN = tokens.get("csrf_token")
        self.WORLD = tokens.get("world")
        self.TOWN = bb_code_town
        self.headers = {
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        }
        self.cookies = {"sid": f"{self.CSRF_TOKEN}"}

    def get_resources_available(self):
        url = f"https://{self.WORLD}.grepolis.com/game/frontend_bridge?town_id={self.TOWN}&action=execute&h={self.H_TOKEN}& \
        json=%7B%22model_url%22%3A%22PremiumExchange%22%2C%22action_name%22%3A%22read%22%2C%22town_id%22%3A{self.TOWN}%2C%22nl_init%22%3Atrue%7D"

        #
        data = {
            'json': f'"model_url":"PremiumExchange","action_name":"read","town_id":{self.TOWN}'}
        r = requests.get(url, headers=self.headers,
                         cookies=self.cookies, data=data)
        data = json.loads(r.text)

        if data["json"].get("error") is not None:
            raise Exception(data["json"]["error"])

        wood = data["json"]["wood"]["capacity"] - data["json"]["wood"]["stock"]
        iron = data["json"]["iron"]["capacity"] - data["json"]["iron"]["stock"]
        stone = data["json"]["stone"]["capacity"] - \
            data["json"]["stone"]["stock"]

        return wood, iron, stone

    def sell_resources_for_gold(self, resource, resource_amount):
        url = f"https://{self.WORLD}.grepolis.com/game/frontend_bridge?town_id={self.TOWN}&action=execute&h={self.H_TOKEN}"
        data = {"json": '{"model_url":"PremiumExchange","action_name":"requestOffer","arguments":{"type":"sell","gold":%s,"%s":%s},"town_id":%s}' % (
            "100", resource, resource_amount, self.TOWN)}
        r = requests.post(url, headers=self.headers,
                          cookies=self.cookies, data=data)
        return json.loads(r.text)["json"]

    def sell_resources_for_gold_response(self, data):
        gold = data["offer"]["gold"]
        resource_type = data["offer"]["resource_type"]
        resource_amount = data["offer"]["resource_amount"]
        captcha_required = data["offer"]["captcha_required"]
        mac = data["mac"]

        if captcha_required:
            hook.send(f"@everyone Captcha is required on world {self.WORLD}")
            print(f"Captcha is required on world {self.WORLD}")

            return False, 0, 0, 0, 0
        else:
            return True, gold, resource_type, resource_amount, mac

    def confirm_offer(self, gold, mac, resource_type, resource_amount):
        url = f"https://{self.WORLD}.grepolis.com/game/frontend_bridge?town_id={self.TOWN}&action=execute&h={self.H_TOKEN}"

        data = {"json": '{"model_url":"PremiumExchange","action_name":"confirmOffer","arguments":{"type":"sell","gold":%s,"mac":"%s","offer_source":"main","%s":%s},"town_id":%s}' % (
            gold, mac, resource_type, resource_amount, self.TOWN)}

        r = requests.post(url, headers=self.headers,
                          cookies=self.cookies, data=data)
        return json.loads(r.text)

    def get_max_to_sell(self) -> int:
        return 0

    def full_trade_cycle(self):
        wood, iron, stone = self.get_resources_available()

        if wood < 300 and iron < 300 and stone < 300:
            print(
                f"[GOLDBOT] [{self.TOWN}] -> [wood: {wood}, iron: {iron}, stone: {stone}]")
            return

        for resource_type in ["wood", "iron", "stone"]:
            print(f"[GOLDBOT] [{self.TOWN}] -> Requesting {resource_type}")
            r = self.sell_resources_for_gold(resource_type, 2000)

            success, gold, resource_type, resource_amount, mac = self.sell_resources_for_gold_response(
                r)
            print(success, gold)
            if not success:
                return
            if success and gold > 0:
                print(
                    f"[GOLDBOT] [{self.TOWN}] -> Trying to sell {resource_amount} {resource_type} for {gold} gold")
                confirm_offer_response = self.confirm_offer(
                    gold, mac, resource_type, resource_amount)
                print(confirm_offer_response)
                json = confirm_offer_response["json"]
                resp = confirm_offer_response["json"]["result"]
                offer = confirm_offer_response["json"]["offer"]
                print(f"[GOLDBOT] [{self.TOWN}] -> Response:  {resp}")

                if resp == "rate_changed":
                    print("Rate changed, trying again...?")
                    r = self.confirm_offer(
                        offer["gold"], json["mac"], offer["resource_type"], offer["resource_amount"])
                    print(r)

            else:
                print(f"Unable to because gold offer: {gold}")

    def run_bot(self):

        while True:
            try:
                self.full_trade_cycle()
                time.sleep(random.randint(20, 40))

            except Exception as e:
                print(e)
                time.sleep(3)
                continue


def main():
    gold_bot = GoldBot(11357)

    gold_bot.run_bot()


if __name__ == "__main__":
    main()
