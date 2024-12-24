from dotenv import load_dotenv
import os
from pathlib import Path

from pydantic_settings import BaseSettings
from os import getenv

load_dotenv()


class Settings(BaseSettings):
    db_url: str = os.getenv('POSTGRES_URL')

    api_v1_prefix: str = '/api/v1'


settings = Settings()
