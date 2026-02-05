FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
RUN pip install uv
COPY pyproject.toml ./
RUN uv pip install --system .

# Copy project
COPY . .

# Expose port
EXPOSE 5000

CMD ["python", "main.py"]
