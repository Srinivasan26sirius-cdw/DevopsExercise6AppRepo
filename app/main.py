from fastapi import FastAPI
from app.logger import setup_loki_logger

logger = setup_loki_logger("fastapi-app")

app = FastAPI()

@app.get("/")
def read_root():
    logger.info("Reading root endpoint")
    return {"message": "Hello from FastAPI!"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    logger.info(f"Fetching item with ID: {item_id}")
    return {"item_id": item_id}
    