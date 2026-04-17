from fastapi import FastAPI
from app.logger import create_logger

# Create logger for this service
logger1 = create_logger("fastapi-service1")
logger2 = create_logger("fastapi-service2")  

app = FastAPI()

@app.get("/")
def read_root():
    logger1.info("Reading root endpoint")
    return {"message": "Hello from FastAPI!"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    logger2.info(f"Fetching item with ID: {item_id}")
    return {"item_id": item_id}
    