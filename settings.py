import os
import sys
from dotenv import load_dotenv


BASE_DIR = './'
def get_env_var(name, default=None):
    try:
        return os.environ[name]
    except KeyError:
        if default:
            return default


def read_env():
    dotenv_path = os.path.join(BASE_DIR, '.env')
    try:
        load_dotenv(dotenv_path)
    except IOError:
        pass


read_env()