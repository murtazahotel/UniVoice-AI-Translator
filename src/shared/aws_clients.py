"""AWS service client wrappers with error handling and retry logic."""

import boto3
from typing import Optional
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from botocore.exceptions import ClientError, BotoCoreError

from .config import get_settings
from .logging import get_logger
from .errors import StorageError, ServiceUnavailableError

logger = get_logger(__name__)


class AWSClientManager:
    """Manages AWS service clients with connection pooling and error handling."""
    
    def __init__(self):
        self.settings = get_settings()
        self._clients: dict[str, any] = {}
    
    def get_client(self, service_name: str) -> any:
        """
        Get or create AWS service client.
        
        Args:
            service_name: AWS service name (e.g., 's3', 'dynamodb')
            
        Returns:
            Boto3 client instance
        """
        if service_name not in self._clients:
            self._clients[service_name] = boto3.client(
                service_name,
                region_name=self.settings.aws_region,
            )
            logger.info("Created AWS client", service=service_name)
        
        return self._clients[service_name]
    
    def get_resource(self, service_name: str) -> any:
        """
        Get or create AWS service resource.
        
        Args:
            service_name: AWS service name (e.g., 's3', 'dynamodb')
            
        Returns:
            Boto3 resource instance
        """
        resource_key = f"{service_name}_resource"
        
        if resource_key not in self._clients:
            self._clients[resource_key] = boto3.resource(
                service_name,
                region_name=self.settings.aws_region,
            )
            logger.info("Created AWS resource", service=service_name)
        
        return self._clients[resource_key]


@lru_cache()
def get_aws_client_manager() -> AWSClientManager:
    """Get cached AWS client manager instance."""
    return AWSClientManager()


class DynamoDBClient:
    """DynamoDB client wrapper with error handling."""
    
    def __init__(self):
        self.manager = get_aws_client_manager()
        self.client = self.manager.get_client("dynamodb")
        self.resource = self.manager.get_resource("dynamodb")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError)),
    )
    def get_item(self, table_name: str, key: dict) -> Optional[dict]:
        """
        Get item from DynamoDB table with retry logic.
        
        Args:
            table_name: DynamoDB table name
            key: Item key
            
        Returns:
            Item data or None if not found
        """
        try:
            table = self.resource.Table(table_name)
            response = table.get_item(Key=key)
            return response.get("Item")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise StorageError(f"Table not found: {table_name}")
            logger.error("DynamoDB get_item failed", error=str(e), table=table_name)
            raise StorageError(f"Failed to get item from {table_name}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError)),
    )
    def put_item(self, table_name: str, item: dict) -> None:
        """
        Put item to DynamoDB table with retry logic.
        
        Args:
            table_name: DynamoDB table name
            item: Item data
        """
        try:
            table = self.resource.Table(table_name)
            table.put_item(Item=item)
        except ClientError as e:
            logger.error("DynamoDB put_item failed", error=str(e), table=table_name)
            raise StorageError(f"Failed to put item to {table_name}")


class S3Client:
    """S3 client wrapper with error handling."""
    
    def __init__(self):
        self.manager = get_aws_client_manager()
        self.client = self.manager.get_client("s3")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError)),
    )
    def upload_file(self, bucket: str, key: str, data: bytes) -> None:
        """
        Upload file to S3 with retry logic.
        
        Args:
            bucket: S3 bucket name
            key: Object key
            data: File data
        """
        try:
            self.client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ServerSideEncryption="AES256",
            )
        except ClientError as e:
            logger.error("S3 upload failed", error=str(e), bucket=bucket, key=key)
            raise StorageError(f"Failed to upload to S3: {bucket}/{key}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError)),
    )
    def download_file(self, bucket: str, key: str) -> bytes:
        """
        Download file from S3 with retry logic.
        
        Args:
            bucket: S3 bucket name
            key: Object key
            
        Returns:
            File data
        """
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise StorageError(f"Object not found: {bucket}/{key}")
            logger.error("S3 download failed", error=str(e), bucket=bucket, key=key)
            raise StorageError(f"Failed to download from S3: {bucket}/{key}")


class KinesisClient:
    """Kinesis client wrapper with error handling."""
    
    def __init__(self):
        self.manager = get_aws_client_manager()
        self.client = self.manager.get_client("kinesis")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError)),
    )
    def put_record(self, stream_name: str, data: bytes, partition_key: str) -> None:
        """
        Put record to Kinesis stream with retry logic.
        
        Args:
            stream_name: Kinesis stream name
            data: Record data
            partition_key: Partition key for sharding
        """
        try:
            self.client.put_record(
                StreamName=stream_name,
                Data=data,
                PartitionKey=partition_key,
            )
        except ClientError as e:
            logger.error("Kinesis put_record failed", error=str(e), stream=stream_name)
            raise ServiceUnavailableError("kinesis", "Failed to publish to stream")


@lru_cache()
def get_dynamodb_client() -> DynamoDBClient:
    """Get cached DynamoDB client instance."""
    return DynamoDBClient()


@lru_cache()
def get_s3_client() -> S3Client:
    """Get cached S3 client instance."""
    return S3Client()


@lru_cache()
def get_kinesis_client() -> KinesisClient:
    """Get cached Kinesis client instance."""
    return KinesisClient()
