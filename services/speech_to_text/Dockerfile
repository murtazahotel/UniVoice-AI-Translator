# Speech-to-Text Service Dockerfile
FROM univoice-base:latest

# Copy service code
COPY src/services/speech_to_text /app/src/services/speech_to_text
COPY src/services/speech_to_text/main.py /app/main.py

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
