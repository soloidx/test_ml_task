import asyncio
import logging
import os
import time

import aiohttp
from redis import Redis
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


def print_results(_results):
    """
    This method prints only the 3 first results
    """
    order = ["Top", "Second", "Third"]

    for index, ele in enumerate(_results):
        print(
            f"{order[index]} match: \"{ele['name']}\" "
            f"with score: {ele['score']:.8f}"
        )
    print("\n")


def clasify_image_sync(*args, **kwargs):
    asyncio.run(clasify_image(*args, **kwargs))


async def clasify_image(image_URL):
    classifier = BirdClassifier(settings=settings)
    classifier.initialize()

    async with aiohttp.ClientSession() as session:
        result = await classifier.classify_bird(image_URL, session)
        print_results(result)


if __name__ == "__main__":
    logging.info("Starting...")
    queue = Queue(connection=Redis(settings.redis_DSN))
    for image in image_urls:
        clasify_image_sync(image)
