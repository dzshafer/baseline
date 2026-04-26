FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Flask
RUN pip install flask --no-cache-dir

# Copy app files
COPY server.py .
COPY public/ ./public/

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 3000

# Run
CMD ["python3", "server.py"]
