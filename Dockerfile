FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# RUN alembic upgrade head
EXPOSE 5005
# CMD ["python", "main.py"]
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
