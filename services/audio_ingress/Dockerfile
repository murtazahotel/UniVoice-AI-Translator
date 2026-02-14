# Audio Ingress Service Dockerfile
FROM univoice-base:latest

# Copy service code
COPY src/services/audio_ingress /app/src/services/audio_ingress
COPY src/services/audio_ingress/main.py /app/main.py

# Expose WebSocket port
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
