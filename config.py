import os
import logging
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask
from motor.motor_asyncio import AsyncIOMotorClient
from asgiref.wsgi import WsgiToAsgi

load_dotenv()

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)

if not os.path.exists('logs'):
    os.makedirs('logs')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'kubiya')

try:
    client = AsyncIOMotorClient(MONGO_URI)
    logging.info("Connected to MongoDB successfully.")
except Exception as e:
    logging.info(f"Failed to connect to MongoDB: {str(e)}")

db = client[DB_NAME]
metrics_collection = db["metrics"]
metrics_objectID = ObjectId("674d77e62034f74473b1e65f")
cache_collection = db["cache"]

START_DATE = "2018-01-01"
END_DATE = "2023-12-31"
