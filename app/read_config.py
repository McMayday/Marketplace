"""
Инициализация конфигурации.
"""
import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH = os.environ.get('CONFIG_PATH', os.path.join(BASE_DIR, 'sample.env'))

load_dotenv(dotenv_path=CONFIG_PATH, verbose=True)

PROJECT_NAME = os.environ['PROJECT_NAME']
