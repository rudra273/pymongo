from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

uri = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@mongodb-cluster.ovjkv.mongodb.net/?retryWrites=true&w=majority&appName=mongodb-cluster"

client = MongoClient(uri)
db = client.fastapi_crud

def get_db():
    return db