# Use a lightweight official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the data science requirements file into the container
COPY requirements.txt .

# Install data science requirements along with the FastAPI web server dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn websockets httpx python-dotenv

# Copy the API package modules
COPY api/ /app/api/

# Copy the Notebooks folder which contains the decision_tree_scode.pkl model
COPY Notebooks/ /app/Notebooks/

# Copy the run script
COPY run.py .

# Expose port (Google Cloud Run will inject and override this with the $PORT env variable)
EXPOSE 8080

# Run uvicorn server, binding to the port specified by Google Cloud Run ($PORT)
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
