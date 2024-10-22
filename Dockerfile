FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./order_api /app/order_api

# Expose the port
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "order_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
