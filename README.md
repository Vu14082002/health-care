# LUNG HEALTH CARE API

## Run

-   Before run: you must create python environment: `python3 -m venv venv`
-   Then, you active env: `source ./venv/bin/active`
-   Install dependency package: `pip3 install -r requirements.txt --no-cache`
-   Finally, you can run: `python3 main.py`

## Migrate database

-   Create migrate file: `alembic revision --autogenerate -m "<message>"`
-   Update to database: `alembic upgrade head`

# lung-heatlh-care

deploy
docker build -t sherlockvufullsnack/lung-health_care-api:latest .
docker push sherlockvufullsnack/lung-health_care-api:latest
