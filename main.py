import uvicorn

from src.application import app

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5005, reload=True)
