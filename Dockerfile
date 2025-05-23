FROM python:3.12-slim

# Define work directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
# Install dependencies and extras (uploads, JWT, password hashing, Pydantic settings)
RUN pip install --no-cache-dir \
    -r requirements.txt \
    uvicorn \
    gunicorn \
    python-multipart \
    python-jose \
    passlib[bcrypt] \
    pydantic-settings

# Copy project files
COPY . .

# Ensure output is logged immediately
ENV PYTHONUNBUFFERED=1

# Expose port used by the application
EXPOSE 80

# Start the app with Gunicorn and Uvicorn workers
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
