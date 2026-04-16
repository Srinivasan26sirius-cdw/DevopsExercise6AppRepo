import logging
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi-app")

app = FastAPI()

@app.get("/")
def read_root():
    logger.info("Reading root endpoint")
    return {"message": "Hello from FastAPI!"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    logger.info(f"Fetching item with ID: {item_id}")
    return {"item_id": item_id}
    