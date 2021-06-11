import urllib.request
import urllib.error
from operator import itemgetter
from typing import Any

import aiohttp
import cv2  # type: ignore
import numpy as np
import tensorflow.compat.v2 as tf  # type: ignore
import tensorflow_hub as hub  # type: ignore

from . import exceptions


class BirdClassifier:
    def __init__(self, model_URL: str, labels_URL: str) -> None:
        if not model_URL:
            raise exceptions.BadConfigurationError(
                "You need to specify the model URL"
            )

        if not labels_URL:
            raise exceptions.BadConfigurationError(
                "You need to specify the labels URL"
            )

        self.model_URL = model_URL
        self.model: hub.KerasLayer = None
        self.labels_URL = labels_URL
        self.labels = None

    def initialize(self):
        self.__load_model()  # TODO: test against connection errors
        try:
            self.__load_labels()
        except urllib.error.HTTPError as e:
            raise exceptions.InitializationError(
                "Cannot download the labels"
            ) from e

    def __load_model(self):
        self.model = hub.KerasLayer(self.model_URL)

    def __load_labels(self):
        with urllib.request.urlopen(self.labels_URL) as response:

            bird_labels_lines = [
                line.decode("utf-8").replace("\n", "")
                for line in response.readlines()
            ]
            bird_labels_lines.pop(0)  # remove header (id, name)
            birds = {}
            for bird_line in bird_labels_lines:
                bird_id = int(bird_line.split(",")[0])
                bird_name = bird_line.split(",")[1]
                birds[bird_id] = {"name": bird_name}

            self.labels = birds

    async def classify_batch(self, image_urls):
        async with aiohttp.ClientSession() as session:
            for index, image_url in enumerate(image_urls):
                print("Run: %s" % int(index + 1))
                await self.classify_bird(image_url, session)

    async def classify_bird(self, image_url, session):
        if not self.model or not self.labels:
            raise exceptions.InitializationError(
                "The classifier is not configured"
            )

        image_array = await self.__download_image(image_url, session)
        image = self.__preprocess_image(image_array)

        model_raw_output = self.__call_model(image)
        self.get_top_birds(model_raw_output)
        top_birds = self.get_top_birds(model_raw_output)
        self.__print_results(top_birds)

    @staticmethod
    async def __download_image(image_url: str, session: Any) -> np.ndarray:
        # TODO: add error management
        async with session.get(image_url) as response:
            return np.asarray(bytearray(await response.read()), dtype=np.uint8)

    @staticmethod
    def __preprocess_image(image_array: np.ndarray) -> Any:
        # TODO: image as null
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (224, 224))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image / 255
        return image

    def __call_model(self, image: Any):
        image_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
        image_tensor = tf.expand_dims(image_tensor, 0)
        model_raw_output = self.model.call(image_tensor).numpy()
        return model_raw_output

    def get_top_birds(self, model_raw_output, top=3):
        result = []
        model_result = sorted(
            np.ndenumerate(model_raw_output), key=itemgetter(1), reverse=True
        )[:top]
        for ele in model_result:
            result.append(dict({"score": ele[1]}, **self.labels[ele[0][1]]))
        return result

    @staticmethod
    def __print_results(results):
        """
        This method prints only the 3 first results
        """
        order = ["Top", "Second", "Third"]

        for index, ele in enumerate(results):
            print(
                f"{order[index]} match: \"{ele['name']}\" with score: {ele['score']:.8f}"
            )
        print("\n")
