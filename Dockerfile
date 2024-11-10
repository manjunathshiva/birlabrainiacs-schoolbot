# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME="/opt/poetry"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Add Poetry to PATH
ENV PATH="${POETRY_HOME}/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml  README.md ./
COPY src/ ./src/
COPY data/ ./data/
COPY frontend.py ingestion.py ./


# Install dependencies
RUN poetry install


# Copy environment variables file
COPY .env.example .env

# Create startup script
RUN echo '#!/bin/bash\n\
poetry run services & \n\
poetry run app & \n\
poetry run streamlit run frontend.py & \n\
wait' > /app/start.sh && \
chmod +x /app/start.sh

# Expose ports for FastAPI and  Streamlit
EXPOSE 8000 8501

# Run all services using the startup script
CMD ["/app/start.sh"]
