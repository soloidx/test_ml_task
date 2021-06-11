from typing import Any
import urllib.request

import cv2  # type: ignore
import numpy as np
import tensorflow.compat.v2 as tf  # type: ignore
import tensorflow_hub as hub  # type: ignore


# pylint: disable=E1103
class BirdClassifier:
    def __init__(self, model_URL, labels_URL) -> None:
        if not model_URL:
            raise Exception("You need to specify the model URL")

        if not labels_URL:
            raise Exception("You need to specify the labels URL")

        self.model_URL = model_URL
        self.model: hub.KerasLayer = None
        self.labels_URL = labels_URL
        self.labels = None

    def initialize(self):
        self.__load_model()
        self.__load_labels()

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

    def classify_bird(self, image_url):
        if not self.model or not self.labels:
            raise Exception("The classifier is not configured")

        image_array = self.__download_image(image_url)
        image = self.__preprocess_image(image_array)

        # Generate tensor
        model_raw_output = self.__generate_tensor(image)

        birds_names_with_results_ordered = self.order_birds_by_result_score(
            model_raw_output
        )

        # Print results to kubernetes log
        bird_name, bird_score = self.get_top_n_result(
            1, birds_names_with_results_ordered
        )
        print('Top match: "%s" with score: %s' % (bird_name, bird_score))
        bird_name, bird_score = self.get_top_n_result(
            2, birds_names_with_results_ordered
        )
        print('Second match: "%s" with score: %s' % (bird_name, bird_score))
        bird_name, bird_score = self.get_top_n_result(
            3, birds_names_with_results_ordered
        )
        print('Third match: "%s" with score: %s' % (bird_name, bird_score))
        print("\n")

    @staticmethod
    def __download_image(image_url: str) -> np.ndarray:
        # TODO: add error management
        with urllib.request.urlopen(image_url) as response:
            return np.asarray(bytearray(response.read()), dtype=np.uint8)

    @staticmethod
    def __preprocess_image(image_array: np.ndarray) -> Any:
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (224, 224))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image / 255
        return image

    def __generate_tensor(self, image: Any):
        image_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
        image_tensor = tf.expand_dims(image_tensor, 0)
        model_raw_output = self.model.call(image_tensor).numpy()
        return model_raw_output

    def classify_batch(self, image_urls):
        for index, image_url in enumerate(image_urls):
            print("Run: %s" % int(index + 1))
            self.classify_bird(image_url)

    def order_birds_by_result_score(self, model_raw_output):
        for index, value in np.ndenumerate(model_raw_output):
            bird_index = index[1]
            # FIXME this could be troublesome
            self.labels[bird_index]["score"] = value

        return sorted(self.labels.items(), key=lambda x: x[1]["score"])

    def get_top_n_result(self, top_index, birds_names_with_results_ordered):
        bird_name = birds_names_with_results_ordered[top_index * (-1)][1][
            "name"
        ]
        bird_score = birds_names_with_results_ordered[top_index * (-1)][1][
            "score"
        ]
        return bird_name, bird_score
