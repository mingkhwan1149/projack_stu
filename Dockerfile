# Use an official Python runtime as a parent image
FROM python:3.10-alpine as Prod

# Set the working directory to /app
WORKDIR /usr/src/app

## Install system dependencies
#RUN apk update && \
#    apk add --no-cache tzdata build-base musl-dev gfortran

RUN apk update && \
apk add --no-cache tzdata

ENV TZ Asia/Bangkok

RUN pip install --upgrade pip

# Copy the requirements.txt file to the container
COPY code/requirements.txt /usr/src/app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY code /usr/src/app

# Define the command to run your FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# Expose the port that the FastAPI app will run on
EXPOSE 8080

# Use an official Python runtime as a parent image
FROM python:3.10-alpine as Dev

# Set the working directory to /app
WORKDIR /usr/src/app

## Install system dependencies
#RUN apk update && \
#    apk add --no-cache tzdata build-base musl-dev gfortran

RUN apk update && \
apk add --no-cache tzdata

ENV TZ Asia/Bangkok

RUN pip install --upgrade pip

# Copy the requirements.txt file to the container
COPY code/requirements.txt /usr/src/app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY code /usr/src/app

# Define the command to run your FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# Expose the port that the FastAPI app will run on
EXPOSE 8080