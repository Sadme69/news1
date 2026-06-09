# Use the official Playwright Python image which has all dependencies pre-installed
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (Render provides this via $PORT)
EXPOSE 8000

# Start the application using uvicorn
# We use shell form to allow environment variable substitution for $PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
