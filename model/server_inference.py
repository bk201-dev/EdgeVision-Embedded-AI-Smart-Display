from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

import numpy as np
import cv2
import cvlib as cv
import os
import logging


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)


# ============================================================
# Flask application
# ============================================================

app = Flask(__name__)

# Maximum accepted request size.
# Useful to avoid receiving unexpectedly large images.
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB


# ============================================================
# Configuration
# ============================================================

MODEL_PATH = os.getenv(
    "EDGEVISION_MODEL_PATH",
    "gender_detection.model"
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


# ============================================================
# Load AI model
# ============================================================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}\n"
        "Place the trained model in this directory or set "
        "the EDGEVISION_MODEL_PATH environment variable."
    )


logging.info("Loading AI model...")

model = load_model(MODEL_PATH)

logging.info("Model loaded successfully.")


# ============================================================
# Image preprocessing
# ============================================================

def preprocess_jpg_bytes(jpg_bytes):
    """
    Convert raw JPEG bytes into the same input format used
    by the local webcam inference pipeline.

    Pipeline:

    JPEG
      -> OpenCV BGR image
      -> Face detection
      -> Largest face selection
      -> Face crop
      -> Resize to 96x96
      -> Normalize to [0, 1]
      -> Add batch dimension
    """

    # --------------------------------------------------------
    # JPEG bytes -> NumPy buffer
    # --------------------------------------------------------

    nparr = np.frombuffer(
        jpg_bytes,
        np.uint8
    )


    # --------------------------------------------------------
    # Decode JPEG using OpenCV
    # --------------------------------------------------------

    frame = cv2.imdecode(
        nparr,
        cv2.IMREAD_COLOR
    )

    if frame is None:
        return None


    # --------------------------------------------------------
    # Detect faces
    # --------------------------------------------------------

    faces, confidences = cv.detect_face(frame)

    if len(faces) == 0:
        return None

    largest_face = None
    largest_area = 0

    for face in faces:

        startX, startY = face[0], face[1]
        endX, endY = face[2], face[3]

        width = endX - startX
        height = endY - startY

        area = width * height

        if area > largest_area:
            largest_area = area
            largest_face = face


    if largest_face is None:
        return None


    startX, startY = largest_face[0], largest_face[1]
    endX, endY = largest_face[2], largest_face[3]


    # --------------------------------------------------------
    # Keep coordinates inside image boundaries
    # --------------------------------------------------------

    height, width = frame.shape[:2]

    startX = max(0, startX)
    startY = max(0, startY)

    endX = min(width, endX)
    endY = min(height, endY)


    # --------------------------------------------------------
    # Crop detected face
    # --------------------------------------------------------

    face_crop = np.copy(
        frame[startY:endY, startX:endX]
    )

    if (
        face_crop.shape[0] < 10
        or face_crop.shape[1] < 10
    ):
        return None


    # --------------------------------------------------------
    # Resize to model input resolution
    # --------------------------------------------------------

    face_crop = cv2.resize(
        face_crop,
        (96, 96)
    )


    # --------------------------------------------------------
    # Normalize pixel values
    # --------------------------------------------------------

    face_crop = face_crop.astype(
        "float32"
    ) / 255.0


    # --------------------------------------------------------
    # Convert to Keras image array
    # --------------------------------------------------------

    face_crop = img_to_array(
        face_crop
    )


    # --------------------------------------------------------
    # Add batch dimension
    # --------------------------------------------------------

    face_crop = np.expand_dims(
        face_crop,
        axis=0
    )


    return face_crop


# ============================================================
# Health endpoint
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "EdgeVision AI server running"
    })


# ============================================================
# Prediction endpoint
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # ----------------------------------------------------
        # Read raw JPEG bytes sent by the embedded camera
        # ----------------------------------------------------

        jpg_bytes = request.data


        if not jpg_bytes:

            return jsonify({
                "error": "no image received"
            }), 400


        # ----------------------------------------------------
        # Preprocess image
        # ----------------------------------------------------

        input_tensor = preprocess_jpg_bytes(
            jpg_bytes
        )


        if input_tensor is None:

            return jsonify({
                "error": "no valid face detected or image could not be decoded"
            }), 422


        # ----------------------------------------------------
        # Run CNN inference
        # ----------------------------------------------------

        predictions = model.predict(
            input_tensor,
            verbose=0
        )


        # ----------------------------------------------------
        # Handle two output classifier
        # ----------------------------------------------------

        if (
            predictions.ndim == 2
            and predictions.shape[1] >= 2
        ):

            scores = predictions[0]

            class_index = int(
                np.argmax(scores)
            )

            confidence = float(
                scores[class_index]
            )


        # ----------------------------------------------------
        # Fallback for a one  output sigmoid model
        # ----------------------------------------------------

        else:

            value = float(
                predictions[0][0]
                if predictions.ndim == 2
                else predictions[0]
            )

            class_index = (
                1 if value >= 0.5 else 0
            )

            confidence = (
                value
                if class_index == 1
                else 1.0 - value
            )


        label = LABELS[class_index]


        logging.info(
            "Prediction: %s (%.2f%%)",
            label,
            confidence * 100
        )


        # ----------------------------------------------------
        # JSON response
        # ----------------------------------------------------

        return jsonify({

            "label": label,

            "confidence": confidence,

            "confidence_percent": round(
                confidence * 100,
                2
            )

        })


    except Exception as error:

        logging.exception(
            "Prediction error"
        )

        return jsonify({
            "error": "prediction failed"
        }), 500


# ============================================================
# Start server
# ============================================================

if __name__ == "__main__":

    logging.info(
        "Starting EdgeVision server on %s:%s",
        SERVER_HOST,
        SERVER_PORT
    )

    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=False
    )
