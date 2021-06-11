import os


class Settings:
    model_url = os.getenv(
        "MODEL_URL",
        "https://tfhub.dev/google/aiy/vision/classifier/birds_V1/1",
    )
    labels_url = os.getenv(
        "LABELS_URL",
        "https://www.gstatic.com/aihub/tfhub/labelmaps/aiy_birds_V1_labelmap.csv",
    )
