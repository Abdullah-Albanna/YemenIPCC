import os
from pydantic_settings import BaseSettings


from utils.get_app_dir import getExecutablePath


class Env(BaseSettings):
    repo: str = 'Abdullah-Albanna/YemenIPCC'
    secret: str = 'hidden'
    api_domain: str = "https://api.abdurive.online"
    api_key: str = 'hidden_to_protect_from_spam'
    discord_webhook_url: str = 'hidden'
    public_key: str = 'hidden'

    class ConfigDict:
        env_file = os.path.join(getExecutablePath(), ".env")

    class Config:
        env_file = os.path.join(getExecutablePath(), ".env")
