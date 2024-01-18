import os
from dotenv import load_dotenv
load_dotenv()
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CONFIG_DIR)

DATA_DIR = os.path.join(BASE_DIR, 'data')

IMG_PATH = os.path.join(DATA_DIR, 'images')

DB_PATH = os.path.join(DATA_DIR, 'database.db')

PROXY_ROTATE = os.getenv("PROXY_ROTATE", "http://localhost:8089")
PROXY_VERIFY = os.path.join(CONFIG_DIR, 'scrapoxy.crt')

PIXELDRAIN_URL_TYPE = "http://"
PIXELDRAIN_DOMAIN = "50.7.236.50"
PIXELDRAIN_MAX_THREADS = 1
PIXELDRAIN_DELAY_SECONDS = 100
