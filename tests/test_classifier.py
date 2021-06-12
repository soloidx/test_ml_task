import logging
import unittest
import urllib.error
from contextlib import contextmanager
from unittest.mock import PropertyMock, patch

from app.classifier import BirdClassifier, exceptions, logger


@contextmanager
def get_mock_settings(*, model, labels):
    with patch("app.classifier.Settings") as MockSettings:
        type(MockSettings.return_value).model_URL = PropertyMock(
            return_value=model
        )
        type(MockSettings.return_value).labels_URL = PropertyMock(
            return_value=labels
        )
        yield MockSettings()


class TestBirdClassifierInit(unittest.TestCase):
    def test_init_should_setup_fields(self):
        with get_mock_settings(model="foo", labels="bar") as mock_settings:
            classifier = BirdClassifier(settings=mock_settings)
            self.assertEqual(classifier.model_URL, "foo")
            self.assertEqual(classifier.labels_URL, "bar")

    @patch.object(BirdClassifier, "_BirdClassifier__load_model")
    @patch.object(BirdClassifier, "_BirdClassifier__load_labels")
    def test_initialize_should_call_loading_methods(
        self, load_labels_mock, load_model_mock
    ):
        with get_mock_settings(model="foo", labels="bar") as mock_settings:
            classifier = BirdClassifier(settings=mock_settings)
            classifier.initialize()

            load_model_mock.assert_called()
            load_labels_mock.assert_called()

    @patch.object(BirdClassifier, "_BirdClassifier__load_model")
    @patch.object(BirdClassifier, "_BirdClassifier__load_labels")
    def test_initialize_should_throw_initialization_error_on_model(
        self, load_labels_mock, load_model_mock
    ):
        # Dissabling intentionally the logs for this test
        logger.setLevel(logging.CRITICAL)

        with get_mock_settings(model="foo", labels="bar") as mock_settings:
            load_model_mock.side_effect = urllib.error.URLError("Error")
            classifier = BirdClassifier(settings=mock_settings)

            with self.assertRaises(exceptions.InitializationError):
                classifier.initialize()

            load_model_mock.side_effect = AttributeError("Error")
            with self.assertRaises(AttributeError):
                classifier.initialize()

        logger.setLevel(logging.ERROR)

    @patch.object(BirdClassifier, "_BirdClassifier__load_model")
    @patch.object(BirdClassifier, "_BirdClassifier__load_labels")
    def test_initialize_should_throw_initialization_error_on_labels(
        self, load_labels_mock, load_model_mock
    ):
        # Dissabling intentionally the logs for this test
        logger.setLevel(logging.CRITICAL)

        with get_mock_settings(model="foo", labels="bar") as mock_settings:
            load_labels_mock.side_effect = urllib.error.URLError("Error")
            classifier = BirdClassifier(settings=mock_settings)

            with self.assertRaises(exceptions.InitializationError):
                classifier.initialize()

            load_labels_mock.side_effect = AttributeError("Error")
            with self.assertRaises(AttributeError):
                classifier.initialize()

        logger.setLevel(logging.ERROR)
