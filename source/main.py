from city import City
from grepoBot import GrepoBot


def main():
    grepoBot = GrepoBot([City(4970),
                        City(6581, town_type="off_lt"),
                        City(4321, town_type="bir"),
                        City(7238, town_type="def_lt"),
                        City(6706, town_type="vs"),
                        City(7707, town_type="off_lt"),
                        City(6478, town_type="bir"),
                         ]) 

    grepoBot.main()


if __name__ == "__main__":
    main()
