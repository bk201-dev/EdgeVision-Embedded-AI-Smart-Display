# server.py
from flask import Flask, request, jsonify
import numpy as np
import cv2
import tensorflow as tf
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Charge le modèle (même nom que celui que tu utilises localement)
MODEL_PATH = "gender_detection.model"  # ou "model.h5" si tu as .h5
if not os.path.exists(MODEL_PATH):
    logging.error(f"Model not found at {MODEL_PATH}. Place server.py in the same folder as the model.")
else:
    model = tf.keras.models.load_model(MODEL_PATH)
    logging.info(f"Model loaded from {MODEL_PATH}")

# Classe(s) attendue(s)
labels = ["man", "woman"]

def preprocess_jpg_bytes(jpg_bytes):
    # Convert raw JPEG bytes (request.data) -> BGR image -> crop/resize -> normalized array
    nparr = np.frombuffer(jpg_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    # Optionnel : détecter visage et recadrer (ici on assume image contient face ou on crop centre)
    # Pour simplicité : redimensionner tout en 96x96 (comme ton model)
    h, w = img.shape[:2]
    # Si tu veux centrer un crop carré:
    side = min(h, w)
    cx, cy = w // 2, h // 2
    x1 = max(0, cx - side//2)
    y1 = max(0, cy - side//2)
    crop = img[y1:y1+side, x1:x1+side]
    face = cv2.resize(crop, (96, 96))
    face = face.astype("float32") / 255.0
    face = np.expand_dims(face, axis=0)  # shape (1,96,96,3)
    return face

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # ESP32 envoie raw JPEG bytes avec Content-Type: image/jpeg -> on lit request.data
        jpg = request.data
        if not jpg:
            return jsonify({"error": "no image received"}), 400

        x = preprocess_jpg_bytes(jpg)
        if x is None:
            return jsonify({"error": "could not decode image"}), 400

        preds = model.predict(x)  # shape (1,2) or (1,) depending du modèle
        # gère cas sortie float32 ou quantized
        if preds.ndim == 2 and preds.shape[1] >= 2:
            p = preds[0]
            idx = int(np.argmax(p))
            prob = float(p[idx])
        else:
            # si le modèle renvoie une seule probabilité (ex: sigmoid)
            val = float(preds[0][0]) if preds.ndim == 2 else float(preds[0])
            idx = 0 if val < 0.5 else 1
            prob = val if idx == 1 else 1.0 - val

        label = labels[idx]
        return jsonify({"label": label, "prob": prob})
    except Exception as e:
        logging.exception("Prediction error")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Host 0.0.0.0 pour être accessible depuis l'ESP (même réseau)
    app.run(host="0.0.0.0", port=5000)
