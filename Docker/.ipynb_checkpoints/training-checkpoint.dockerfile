# Base image - Python 3.9 (lightweight)
FROM python:3.9-slim

# Set the working directory
WORKDIR /opt/ml/code

# Install basic system dependencies (build-essential is often needed by sklearn)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY Docker/requirements.txt /opt/ml/code/requirements.txt
RUN pip install --upgrade pip && pip install -r /opt/ml/code/requirements.txt

# Copy all source code into the image
COPY . /opt/ml/code/

# Environment variables for clean logging
ENV PYTHONUNBUFFERED=TRUE

# Define the entrypoint — SageMaker calls this when the training job starts
ENTRYPOINT ["python", "/opt/ml/code/src/model_training.py"]
