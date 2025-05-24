from __future__ import annotations

from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    api_v1_prefix: str = "/api/v1"
    project_name: str = "SensorTrackPro"
    version: str = "1.0.0"
    debug: bool = False
    
    # CORS
    allowed_origins: list[str] = ["*"]
    allowed_methods: list[str] = ["*"]
    allowed_headers: list[str] = ["*"]
    
    class Config:
        env_prefix = "API_"


api_settings = APISettings()
