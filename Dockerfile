# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME transcriber
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run app.py when the container launches
#CMD ["python", "app.py"]
CMD flask run -h 0.0.0.0 -p 8080