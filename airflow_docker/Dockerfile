FROM apache/airflow:2.9.1

# Switch to the root user to install system dependencies
USER root

# Install required system libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Clean up apt cache to reduce image size
RUN rm -rf /var/lib/apt/lists/*

# Switch back to the airflow user
USER airflow

# Copy and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt
