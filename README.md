# HEALTH CARE API

## Getting Started

### Prerequisites

-   Python 3.10
-   OS: UBUNTU
-   Docker (for deployment)

### Installation

1. Create a Python virtual environment:

    ```
    python3 -m venv venv
    ```

2. Activate the virtual environment:

    ```
    source ./venv/bin/activate
    ```

3. Install dependencies:

    ```
    pip3 install -r requirements.txt --no-cache
    ```

### Running the Application

1. To start the application run:

    ```
    python3 main.py
    ```

## Database Migration

To manage database migrations, use the following Alembic commands:

1. Create a new migration:

    ```
    alembic revision --autogenerate -m "<descriptive_message>"
    ```

2. Apply migrations:

    ```
    alembic upgrade head
    ```

## API Documentation

1. Access the API documentation at:

    ```
    http://localhost:5005/docs
    ```

## Deployment

To deploy the application using Docker:

1. Build the Docker image:

    ```
    docker build -t sherlockvufullsnack/health_care-api:latest .
    ```

2. Push the image to Docker Hub:

    ```
    docker push sherlockvufullsnack/health_care-api:latest
    ```
