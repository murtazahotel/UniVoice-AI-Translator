# UniVoice Real-Time Speech Translation Platform

Production-ready real-time speech-to-speech translation platform built on AWS infrastructure.

## Architecture

UniVoice follows a microservices architecture with the following services:

- **Audio Ingress Service**: Handles WebSocket audio streaming and buffering
- **Speech-to-Text Service**: Real-time transcription using Amazon Transcribe
- **Translation Service**: Neural machine translation using Amazon Translate
- **Voice Profile Service**: Voice embedding extraction and management
- **Voice Cloning Service**: ML-based voice synthesis with identity preservation
- **Session Manager Service**: Session lifecycle and state management
- **Audio Egress Service**: Streaming translated audio output
- **Authentication Service**: User authentication and authorization

## Setup

### Prerequisites

- Python 3.11+
- AWS Account with configured credentials
- Docker (for containerized deployment)

### Installation

Using Poetry (recommended):
```bash
poetry install
poetry shell
```

Using pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Set environment variables or use AWS Systems Manager Parameter Store:

```bash
export AWS_REGION=us-east-1
export ENVIRONMENT=development
export LOG_LEVEL=INFO
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
ruff check .
```

### Type Checking

```bash
mypy src/
```

## Deployment

Build Docker images:
```bash
docker build -t univoice-audio-ingress -f services/audio_ingress/Dockerfile .
```

## License

Proprietary
