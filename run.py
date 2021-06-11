import logging
import os
import time
import asyncio

from app.classifier import BirdClassifier

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Disable Tensorflow logging

model_url = "https://tfhub.dev/google/aiy/vision/classifier/birds_V1/1"
labels_url = (
    "https://www.gstatic.com/aihub/tfhub/labelmaps/aiy_birds_V1_labelmap.csv"
)

image_urls = [
    "https://upload.wikimedia.org/wikipedia/commons/c/c8/Phalacrocorax_varius_-Waikawa%2C_Marlborough%2C_New_Zealand-8.jpg",
    "https://quiz.natureid.no/bird/db_media/eBook/679edc606d9a363f775dabf0497d31de8c3d7060.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/8/81/Eumomota_superciliosa.jpg",
    "https://i.pinimg.com/originals/f3/fb/92/f3fb92afce5ddff09a7370d90d021225.jpg",
    "https://cdn.britannica.com/77/189277-004-0A3BC3D4.jpg",
]

if __name__ == "__main__":
    # TODO: add logging here and a nice try catch
    loop = asyncio.get_event_loop()

    start_time = time.time()
    classifier = BirdClassifier(model_URL=model_url, labels_URL=labels_url)
    logging.info("Starting...")
    classifier.initialize()
    print("Time spent initializing: %s" % (time.time() - start_time))
    loop.run_until_complete(classifier.classify_batch(image_urls))
    print("Time spent: %s" % (time.time() - start_time))
