from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str

    @property
    def params(self):
        return {
            self.BOT_TOKEN
        }

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()