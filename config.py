from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    bot_token: str
    
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "finance_bot_db"
    db_user: str = "postgres"
    db_password: str = "123"
    
    coingecko_api_url: str = "https://api.coingecko.com/api/v3"
    alpha_vantage_api_key: Optional[str] = None
    alpha_vantage_api_url: str = "https://www.alphavantage.co/query"
    
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()
