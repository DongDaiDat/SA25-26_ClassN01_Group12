from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "UniMIS"
    environment: str = "dev"
    secret_key: str = "change-me"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/unimis"

    # Gmail SMTP
    mail_host: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_use_tls: bool = True
    mail_username: str = ""
    mail_app_password: str = ""
    mail_from_name: str = "UniMIS"
    mail_from_address: str = ""

    report_output_dir: str = "./data/reports"
    template_dir: str = "./app/templates"
    libreoffice_bin: str = "soffice"

settings = Settings()
