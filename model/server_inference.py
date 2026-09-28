from flask import Flask, request, jsonify

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Input,
    Conv2D,
    MaxPooling2D,
    Activation,
    Flatten,
    Dropout,
    Dense,
    BatchNormalization
)
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras import backend as K

import numpy as np
import cv2
import cvlib as cv
import logging
import os


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


MODEL_PATH = os.getenv(
    "EDGEVISION_MODEL_PATH",
    "gender_detection.h5"
)

LABELS = [
    "man",
    "woman"
]

SERVER_HOST = os.getenv(
    "EDGEVISION_HOST",
    "127.0.0.1"
)

SERVER_PORT = int(
    os.getenv(
        "EDGEVISION_PORT",
        "5000"
    )
)


def build_model(
    width=96,
    height=96,
    depth=3,
    classes=2
):

    channel_dim = -1

    if K.image_data_format() == "channels_first":
        input_shape = (depth, height, width)
        channel_dim = 1
    else:
        input_shape = (height, width, depth)

    model = Sequential()

    model.add(
        Input(shape=input_shape)
    )

    model.add(
        Conv2D(
            32,
            (3, 3),
            padding="same"
        )
    )

    model.add(Activation("relu"))
    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )

    model.add(
        MaxPooling2D(
            pool_size=(3, 3)
        )
    )

    model.add(
        Dropout(0.25)
    )


    model.add(
        Conv2D(
            64,
            (3, 3),
            padding="same"
        )
    )

    model.add(Activation("relu"))

    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )


    model.add(
        Conv2D(
            64,
            (3, 3),
            padding="same"
        )
    )

    model.add(Activation("relu"))

    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )

    model.add(
        MaxPooling2D(
            pool_size=(2, 2)
        )
    )

    model.add(
        Dropout(0.25)
    )


    model.add(
        Conv2D(
            128,
            (3, 3),
            padding="same"
        )
    )

    model.add(Activation("relu"))

    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )


    model.add(
        Conv2D(
            128,
            (3, 3),
            padding="same"
        )
    )

    model.add(Activation("relu"))

    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )

    model.add(
        MaxPooling2D(
            pool_size=(2, 2)
        )
    )

    model.add(
        Dropout(0.25)
    )


    model.add(
        Flatten()
    )

    model.add(
        Dense(1024)
    )

    model.add(
        Activation("relu")
    )

    model.add(
        BatchNormalization()
    )

    model.add(
        Dropout(0.5)
    )


    model.add(
        Dense(classes)
    )

    model.add(
        Activation("sigmoid")
    )

    return model


if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )


logging.info(
    "Building CNN architecture..."
)

model = build_model()

logging.info(
    "Loading trained weights..."
)

model.load_weights(
    MODEL_PATH
)

logging.info(
    "Model ready."
)


def preprocess_image(jpg_bytes):

    buffer = np.frombuffer(
        jpg_bytes,
        np.uint8
    )

    frame = cv2.imdecode(
        buffer,
        cv2.IMREAD_COLOR
    )

    if frame is None:
        return None


    faces, _ = cv.detect_face(
        frame
    )

    if len(faces) == 0:
        return None


    largest_face = max(
        faces,
        key=lambda face:
            (face[2] - face[0])
            *
            (face[3] - face[1])
    )


    startX = largest_face[0]
    startY = largest_face[1]

    endX = largest_face[2]
    endY = largest_face[3]


    height, width = frame.shape[:2]


    startX = max(
        0,
        startX
    )

    startY = max(
        0,
        startY
    )

    endX = min(
        width,
        endX
    )

    endY = min(
        height,
        endY
    )


    face = frame[
        startY:endY,
        startX:endX
    ]


    if (
        face.shape[0] < 10
        or
        face.shape[1] < 10
    ):
        return None


    face = cv2.resize(
        face,
        (96, 96)
    )

    face = face.astype(
        "float32"
    ) / 255.0

    face = img_to_array(
        face
    )

    face = np.expand_dims(
        face,
        axis=0
    )

    return face


@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({
        "status":
        "EdgeVision AI server running"
    })


@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        if not request.data:

            return jsonify({
                "error":
                "no image received"
            }), 400


        input_tensor = preprocess_image(
            request.data
        )


        if input_tensor is None:

            return jsonify({
                "error":
                "no valid face detected"
            }), 422


        predictions = model.predict(
            input_tensor,
            verbose=0
        )


        scores = predictions[0]


        class_index = int(
            np.argmax(scores)
        )


        confidence = float(
            scores[class_index]
        )


        label = LABELS[
            class_index
        ]


        logging.info(
            "%s - %.2f%%",
            label,
            confidence * 100
        )


        return jsonify({

            "label":
                label,

            "confidence":
                confidence,

            "confidence_percent":
                round(
                    confidence * 100,
                    2
                )
        })


    except Exception:
    logging.exception("Prediction failed")

    return jsonify({
        "error": "prediction failed"
    }), 500


if __name__ == "__main__":

    logging.info(
        "Server: http://%s:%s",
        SERVER_HOST,
        SERVER_PORT
    )

    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=False
    )