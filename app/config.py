from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://localhost/meshtastic"
    redis_url: Optional[str] = None
    
    # Meshtastic Device
    serial_port: Optional[str] = None  # Auto-detect if None
    device_baud: int = 115200
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    ws_port: int = 8001
    log_level: str = "INFO"
    debug: bool = False
    
    # Service Configuration
    service_channel: int = 7
    command_prefix: str = "!"
    command_timeout: int = 30
    
    # Security
    secret_key: str = "change-this-in-production"
    api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()