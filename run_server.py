import asyncio
import logging
import os
import time

import aiohttp
import redis
from rq import Queue

from app.classifier import BirdClassifier
from app.settings import Settings

settings = Settings()

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Disable Tensorflow logging

image_urls = [
    "https://upload.wikimedia.org/wikipedia/commons/c/c8/Phalacrocorax_varius_-Waikawa%2C_Marlborough%2C_New_Zealand-8.jpg",
    "https://quiz.natureid.no/bird/db_media/eBook/679edc606d9a363f775dabf0497d31de8c3d7060.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/8/81/Eumomota_superciliosa.jpg",
    "https://i.pinimg.com/originals/f3/fb/92/f3fb92afce5ddff09a7370d90d021225.jpg",
    "https://cdn.britannica.com/77/189277-004-0A3BC3D4.jpg",
]

if __name__ == "__main__":
    logging.info("Starting...")
    conn = redis.from_url(settings.redis_DSN)
    queue = Queue("high_priority", connection=conn)
    for image in image_urls:
        print("queueing ", image)
        queue.enqueue(BirdClassifier.classify_bird_sync, settings, image)
