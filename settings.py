from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str

    NAME_DATABASE: str

    @property
    def params(self):
        return {
            "BOT_TOKEN": self.BOT_TOKEN,
            "NAME_DATABASE": self.NAME_DATABASE,
        }

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()