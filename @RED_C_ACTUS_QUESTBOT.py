import concurrent.futures
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from os import system
from json import loads, JSONDecodeError
from uuid import uuid4
from time import sleep
import sys

required_packages = ['requests']

def package_installed(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

for package in required_packages:
    if not package_installed(package):
        print(f"Installing {package}...")
        subprocess.call(['pip', 'install', package])

r = '\033[1;31m'
g = '\033[32;1m'
y = '\033[1;33m'
w = '\033[1;37m'

system("clear")

print(f"{y}[+]{g}Bot created by {r}RED CACTUS")
print(f"{y}[+]{g}Bot version: 1.0")

restore_key = input(f"{y}[+]{g}Enter restore key:{w} ")

# Create connection pool and configure session
pool_size = 10
pool_connections = 10
pool_max_retries = 5
pool_backoff_factor = 0.1

connection_pool = HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_size,
                              max_retries=Retry(total=pool_max_retries, backoff_factor=pool_backoff_factor))

session = requests.Session()
session.mount('http://', connection_pool)
session.mount('https://', connection_pool)
session.headers.update({
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 13; 23049PCD8G Build/TKQ1.221114.001)',
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
})

def load():
    data = {
        'game_version': '1.7.10655',
        'device_name': 'unknown',
        'os_version': '10',
        'model': 'SM-A750F',
        'udid': str(uuid4().int),
        'store_type': 'iraqapps',
        'restore_key': restore_key,
        'os_type': 2
    }
    return loads(session.post('http://iran.fruitcraft.ir/player/load', data=data, timeout=10).text)

def battle_quest(cards, q, hero_id=None):
    data = {'cards': ','.join(map(str, cards))}
    return loads(session.get('http://iran.fruitcraft.ir/battle/quest', params=data, timeout=10).text)

def update_cards(cards):
    if cards:
        cards.append(cards[0])
        cards.pop(0)

load_data = load()
cards = [card['id'] for card in load_data['data']['cards'] if card['power'] < 100]

if len(cards) < 20:
    print(f"{r}You have less than 20 cards!{w}")
    sys.exit()

def quest():
    q = load_data['data']['q']
    count = 0
    xp = 0
    gold = 0
    level = load_data['data']['level']

    retrying_strategy = Retry(total=5, backoff_factor=0.1)
    adapter = HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_size, max_retries=retrying_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            try:
                count += 1
                future = executor.submit(battle_quest, [cards[0]], q)
                q = future.result()
                update_cards(cards)

                if q['status']:
                    xp += q['data']['xp_added']
                    gold += q['data']['gold_added']

                    if q['data']['xp_added'] == 0:
                        print(f"\n{y}Maemoriat had shod ya Shoma bakhtid {r}Stopping the bot.{w}")
                        sys.exit()
                    elif 'level' in q['data'] and q['data']['level'] > level:
                        level = q['data']['level']
                        print(f"\n{g}Congratulations! You leveled up to level {level}!{w}")
                else:
                    print(q, "\n")

            except JSONDecodeError:
                sleep(5)
                continue
            except KeyboardInterrupt:
                sys.exit()
            except requests.exceptions.RequestException as e:
                print(f"\n{r}An error occurred: {e}. Retrying in 30 seconds...{w}")
                sleep(30)
                continue

            sys.stdout.write(f"\r{y}[+] {w}Wins: {count} {y}[+] {w}Xp: {xp} {y}[+] {w}Gold: {gold}")
            sys.stdout.flush()

quest()
