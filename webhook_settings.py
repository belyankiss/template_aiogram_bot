from pydantic import BaseModel, Field, HttpUrl

class Webhook(BaseModel):
    url: HttpUrl = Field(
        title="Адрес URL для работы webhook.",
        description="Должен быть валидным HTTPS URL, доступным для Telegram.",
        examples=["https://your-domain.com/webhook"]
    )
    path: str = Field(
        default="/webhook",
        title="Путь для обработки webhook-запросов.",
        examples=["/webhook"]
    )
    port: int = Field(
        default=3000,
        ge=1,
        le=65535,
        title="Порт для запуска веб-сервера.",
        examples=[3000, 8443]
    )

