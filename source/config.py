from os import getenv
from dotenv import load_dotenv

load_dotenv()
tokens = {
    "h_token": getenv("H_TOKEN"),
    "csrf_token": getenv("CSRF_TOKEN"),
    "world": getenv("WORLD"),
    "discord_hook": getenv("DISCORD_HOOK")
}