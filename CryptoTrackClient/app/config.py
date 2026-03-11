from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:123Secret_a@postgres:5432/cryptowatchlivedb"
    SECRET_KEY: str = "defaultsecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    COINGECKO_API_KEY: str = ""
    COINMARKETCAP_API_KEY: str = ""
    BINANCE_API_KEY: str = ""
    COINCAP_API_KEY: str = ""
    COINSTATS_API_KEY: str = ""
    CRYPTOCOMPARE_API_KEY: str = ""
    KUCOIN_API_KEY: str = ""
    KUCOIN_SECRET_KEY: str = ""
    KUCOIN_PASSPHRASE: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()