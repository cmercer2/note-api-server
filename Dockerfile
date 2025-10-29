FROM python:3.9-slim

# Prevent python from buffering output (helps logs)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy the src directory (keep it as a package so `from src.config` works)
COPY src/ /app/src

# Run from inside the package dir so relative paths for files are consistent
WORKDIR /app/src

# Expose the port the Flask app uses
EXPOSE 12349

CMD ["python", "server.py"]