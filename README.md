# grepoBot

<div id="readme-top"> </div>

<!-- Warning for the user if they get banned I'm not responsible -->
## **!Warning!**
Use at your own risk.  
I'm not responsible if you get banned for using this bot. I personally never got banned using this bot and have been using it for 2+ years so you should be fine.

## About The Project

Bot for grepolis written in Python.  
I personally stopped playing grepolis a couple months ago and therefore stopped working on this project and will probably not be updating this.  
Most of the code is pretty self explanatory.  
I used the bot for over 2 years and never got banned, even when I was sending 10 support/attack requests in a second to time attacks/destroy enemy colony ships.  
There's a limit to the amount of attack requests you can send in a minute which I think is 10.  
There's no limit to the amount of support requests you can send which makes the bot really powerful to save your cities when you know the arrival time of a colony ship.

Features include:

- Sending and timing attacks
- farming villages
- building buildings
- recruiting units
- <p><a href="#goldbot">GoldBot</a> to automatically exchange resources for gold</p>


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

- Version of Python greater than 3.6

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/B1GJ/GrepoBot.git
   ```
2. Install necessary packages
   ```sh
    pip install -r requirements.txt
   ```
3. Create a .env file in the source directory
   ```sh
    touch .env
   ```
3. Copy/paste below and fill in with ur own values.
   ```sh
    WORLD=""
    CSRF_TOKEN=""
    H_TOKEN=""
    DISCORD_HOOK=""
   ```

### How to get the values for the .env file

1. Open grepolis and login to your favorite world.
2. In the top left, the first characters will contain the world name. For example, nl105.  
![Image of world name](source\images\world_config.jpg)
3. Open the network tab in your browser and filter on XHR.
4. Click on any request
5. In the request headers, you will find the CSRF_TOKEN (sid) and H_TOKEN (h_token).
6. Paste these in your .env file.

<!-- USAGE EXAMPLES -->

## Usage



## **main.py**
This is the main file that will run the bot.  
This will instantiate an instance of the GrepoBot class and call the main() method.  
GrepoBot takes a list of City objects as an input.  
City takes the bb_code of the town as an input.  
**Be sure to change all the bb_codes to the bb_codes of your cities.** 

Once you've done that you can just run main.py
```sh
python main.py
```

*Example output running main.py*
![main](source\images\main_example.png)


## **GrepoBot.py**
By default this will:
- Farm all villages of all cities and wait between 600 and 650 cities before starting the next cycle.
- Check for possible buildings to upgrade and upgrade them if possible
- Constantly checks the market to see if it's possible to exchange resources for gold. After 3 times you'll have to manually fill in a captcha. The bot will automatically send a message to a discord Webhook to alert the user when a captcha is required.
- Constantly checks the commands to see if we're getting attacked. If we're getting attacked, it will send a message to a discord Webhook to alert the user. Also possible to automatically dodge an attack (but disabled by default)
![CommandChecker Alert Example](source\images\example_command_checker.jpg)


## **TimeBot.py**
To time attack or support requests. 
<!-- Link to demo youtube video in markdown-->
<iframe width="560" height="315" src="https://www.youtube.com/embed/oVjMQ8C0VtY" title="GrepoBot timebot demo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>


<div id="goldbot"> </div>

## **GoldBot.py**
Constantly checks the market to see if it's possible to exchange resources for gold. After 3 times you'll have to manually fill in a captcha. The bot will automatically send a message to a discord Webhook to alert the user when a captcha is required.

I was able to farm around 500-1000 gold a day using this bot on a single world. You'll make a lot of gold combining the farmbot and this goldbot on a newly started world since a lot of players will be asking for resources in the beginning.
![GoldBot Alert](source\images\example_goldbot.jpg)


## Contact
I'll help the first few people that ran into any issues or have any questions out. Like I said, I stopped playing grepolis a couple months ago so I won't be updating this bot anymore.

Contact me on discord: **jarno#8725**



<p align="right">(<a href="#readme-top">back to top</a>)</p>

