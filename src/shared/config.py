"""Configuration management using environment variables and AWS Systems Manager."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import boto3
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable and SSM Parameter Store support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    enable_xray: bool = Field(default=True, alias="ENABLE_XRAY")
    
    # Service Configuration
    service_name: str = Field(default="univoice", alias="SERVICE_NAME")
    
    # AWS Services
    dynamodb_sessions_table: str = Field(
        default="univoice-sessions", alias="DYNAMODB_SESSIONS_TABLE"
    )
    dynamodb_voice_profiles_table: str = Field(
        default="univoice-voice-profiles", alias="DYNAMODB_VOICE_PROFILES_TABLE"
    )
    dynamodb_users_table: str = Field(
        default="univoice-users", alias="DYNAMODB_USERS_TABLE"
    )
    
    s3_voice_embeddings_bucket: str = Field(
        default="univoice-voice-embeddings", alias="S3_VOICE_EMBEDDINGS_BUCKET"
    )
    s3_recordings_bucket: str = Field(
        default="univoice-session-recordings", alias="S3_RECORDINGS_BUCKET"
    )
    
    kinesis_audio_stream: str = Field(
        default="univoice-audio-stream", alias="KINESIS_AUDIO_STREAM"
    )
    
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_ssl: bool = Field(default=True, alias="REDIS_SSL")
    
    # API Configuration
    api_gateway_endpoint: Optional[str] = Field(default=None, alias="API_GATEWAY_ENDPOINT")
    websocket_endpoint: Optional[str] = Field(default=None, alias="WEBSOCKET_ENDPOINT")
    
    # Performance
    max_concurrent_sessions: int = Field(default=1000, alias="MAX_CONCURRENT_SESSIONS")
    session_timeout_seconds: int = Field(default=7200, alias="SESSION_TIMEOUT_SECONDS")
    
    # SSM Parameter Store prefix
    ssm_parameter_prefix: str = Field(
        default="/univoice", alias="SSM_PARAMETER_PREFIX"
    )


class ConfigManager:
    """Manages configuration from environment variables and AWS SSM Parameter Store."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._ssm_client: Optional[boto3.client] = None
        self._parameter_cache: dict[str, str] = {}

    @property
    def ssm_client(self) -> boto3.client:
        """Lazy initialization of SSM client."""
        if self._ssm_client is None:
            self._ssm_client = boto3.client(
                "ssm", region_name=self.settings.aws_region
            )
        return self._ssm_client

    def get_parameter(self, parameter_name: str, use_cache: bool = True) -> Optional[str]:
        """
        Retrieve parameter from SSM Parameter Store.
        
        Args:
            parameter_name: Name of the parameter (without prefix)
            use_cache: Whether to use cached value
            
        Returns:
            Parameter value or None if not found
        """
        full_path = f"{self.settings.ssm_parameter_prefix}/{parameter_name}"
        
        if use_cache and full_path in self._parameter_cache:
            return self._parameter_cache[full_path]
        
        try:
            response = self.ssm_client.get_parameter(
                Name=full_path, WithDecryption=True
            )
            value = response["Parameter"]["Value"]
            self._parameter_cache[full_path] = value
            return value
        except self.ssm_client.exceptions.ParameterNotFound:
            return None
        except Exception as e:
            # Log error but don't fail - fall back to environment variables
            print(f"Error retrieving SSM parameter {full_path}: {e}")
            return None

    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Retrieve secret from AWS Secrets Manager.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            Secret value or None if not found
        """
        try:
            secrets_client = boto3.client(
                "secretsmanager", region_name=self.settings.aws_region
            )
            response = secrets_client.get_secret_value(SecretId=secret_name)
            return response["SecretString"]
        except Exception as e:
            print(f"Error retrieving secret {secret_name}: {e}")
            return None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


@lru_cache()
def get_config_manager() -> ConfigManager:
    """Get cached config manager instance."""
    return ConfigManager(get_settings())
