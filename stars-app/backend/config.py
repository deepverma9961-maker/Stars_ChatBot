from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), extra="ignore")

    databricks_host: str = ""
    databricks_http_path: str = ""
    databricks_token: str = ""
    catalog: str = "aiagenticdemo"
    schema_gold: str = "stars_gold"
    schema_silver: str = "stars_silver"
    schema_bronze: str = "stars_bronze"

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    sendgrid_api_key: str = ""
    sendgrid_from_email: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5"

    app_base_url: str = ""

    @property
    def gold(self) -> str:
        return f"{self.catalog}.{self.schema_gold}"

    @property
    def silver(self) -> str:
        return f"{self.catalog}.{self.schema_silver}"

    @property
    def bronze(self) -> str:
        return f"{self.catalog}.{self.schema_bronze}"


settings = Settings()
