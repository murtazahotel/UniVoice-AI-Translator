# UniVoice Project Architecture

## Project Structure

```
univoice/
├── src/
│   ├── shared/                      # Shared utilities and common functionality
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration management (env vars + SSM)
│   │   ├── logging.py              # Structured logging with CloudWatch
│   │   ├── tracing.py              # AWS X-Ray distributed tracing
│   │   ├── errors.py               # Custom exception classes
│   │   └── aws_clients.py          # AWS service client wrappers
│   │
│   └── services/                    # Microservices
│       ├── audio_ingress/          # WebSocket audio streaming
│       ├── speech_to_text/         # Amazon Transcribe integration
│       ├── translation/            # Amazon Translate integration
│       ├── voice_profile/          # Voice embedding extraction
│       ├── voice_cloning/          # ML-based voice synthesis
│       ├── session_manager/        # Session lifecycle management
│       ├── audio_egress/           # Audio output streaming
│       └── authentication/         # User auth and authorization
│
├── services/                        # Docker configurations per service
│   ├── audio_ingress/
│   │   └── Dockerfile
│   ├── speech_to_text/
│   │   └── Dockerfile
│   └── ...
│
├── tests/                          # Test suite
│   ├── shared/                     # Tests for shared utilities
│   └── services/                   # Tests for microservices
│
├── scripts/                        # Setup and utility scripts
│   ├── setup.sh                    # Linux/Mac setup script
│   └── setup.ps1                   # Windows setup script
│
├── .kiro/                          # Kiro spec files
│   └── specs/
│       └── univoice/
│
├── pyproject.toml                  # Poetry configuration
├── requirements.txt                # Pip dependencies
├── Dockerfile.base                 # Base Docker image
├── docker-compose.yml              # Local development environment
├── Makefile                        # Development commands
├── .env.example                    # Environment variable template
└── README.md                       # Project documentation
```

## Shared Utilities

### Configuration Management (`src/shared/config.py`)
- Environment variable loading with Pydantic
- AWS Systems Manager Parameter Store integration
- AWS Secrets Manager integration
- Cached configuration instances

### Logging (`src/shared/logging.py`)
- Structured JSON logging for CloudWatch
- Correlation ID tracking
- Log level configuration
- Error logging with context

### Tracing (`src/shared/tracing.py`)
- AWS X-Ray integration
- Distributed tracing across services
- Function-level tracing decorators
- Trace annotations and metadata

### Error Handling (`src/shared/errors.py`)
- Custom exception hierarchy
- Standard error codes
- HTTP status code mapping
- Error serialization for API responses

### AWS Clients (`src/shared/aws_clients.py`)
- DynamoDB client with retry logic
- S3 client with encryption
- Kinesis client for streaming
- Connection pooling and caching

## Microservices Architecture

Each service follows a consistent structure:
- Independent deployment unit
- Dedicated Dockerfile
- Service-specific configuration
- Health check endpoints
- Observability integration

## Development Workflow

1. **Setup**: Run `scripts/setup.sh` (or `setup.ps1` on Windows)
2. **Configuration**: Update `.env` with AWS credentials
3. **Development**: Use `docker-compose` for local services
4. **Testing**: Run `pytest` for unit and integration tests
5. **Deployment**: Build Docker images and deploy to ECS Fargate

## AWS Service Integration

- **DynamoDB**: Session state, voice profiles, user data
- **S3**: Voice embeddings, session recordings
- **Kinesis**: Real-time audio streaming
- **ElastiCache (Redis)**: Caching and rate limiting
- **API Gateway**: REST and WebSocket APIs
- **ECS Fargate**: Container orchestration
- **SageMaker**: ML model hosting
- **CloudWatch**: Metrics and logging
- **X-Ray**: Distributed tracing
- **Cognito**: User authentication
- **Systems Manager**: Configuration management

## Configuration Sources

Configuration is loaded in the following order (later sources override earlier):
1. Default values in `Settings` class
2. `.env` file
3. Environment variables
4. AWS Systems Manager Parameter Store
5. AWS Secrets Manager (for sensitive data)

## Testing Strategy

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test service interactions
- **Property-Based Tests**: Test correctness properties
- **End-to-End Tests**: Test complete workflows

## Security Considerations

- All data encrypted in transit (TLS 1.3)
- All data encrypted at rest (AES-256)
- Least-privilege IAM roles
- Secrets stored in AWS Secrets Manager
- Audit logging for all access
- Rate limiting and DDoS protection
