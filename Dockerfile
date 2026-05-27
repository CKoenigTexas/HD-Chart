FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Swiss Ephemeris files (required for accurate calculations)
# These cover years 1800–2400 which covers all birth dates we'd ever need
RUN mkdir -p /app/ephe && \
    wget -q -O /app/ephe/seas_18.se1 https://github.com/aloistr/swisseph/raw/master/ephe/seas_18.se1 && \
    wget -q -O /app/ephe/semo_18.se1 https://github.com/aloistr/swisseph/raw/master/ephe/semo_18.se1 && \
    wget -q -O /app/ephe/sepl_18.se1 https://github.com/aloistr/swisseph/raw/master/ephe/sepl_18.se1

# Copy application
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
