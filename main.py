import os
import logging
from asgiref.wsgi import WsgiToAsgi
import uvicorn
from config import app, asgi_app 
import routes

if __name__ == "__main__":
    logging.info("Starting Flask app with Uvicorn...")
    uvicorn.run(asgi_app, host="0.0.0.0", port=5000, log_level="info")
