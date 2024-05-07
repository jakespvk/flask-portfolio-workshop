import secrets
from pathlib import Path 


SECRET_KEY = secrets.token_urlsafe(50)
DEBUG = False 
TESTING = False
PROJECT_PATH = Path.cwd()
DB_NAME = 'blogwise_dev.db'
DB_URI = f"{PROJECT_PATH}/{DB_NAME}"

