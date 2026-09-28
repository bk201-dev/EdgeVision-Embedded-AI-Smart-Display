# AI Model

This directory contains the computer-vision model used by **EdgeVision**.

The model is a custom convolutional neural network trained to classify cropped face images into the two labels used by the original training dataset:

- `man`
- `woman`

> The output represents the model's visual classification based on its training data. It should not be interpreted as determining a person's actual gender identity.

---

## Model Pipeline

```text
Input Image
    ↓
Face Detection
    ↓
Face Crop
    ↓
Resize to 96 × 96
    ↓
Normalize / 255
    ↓
CNN
    ↓
Class + Confidence
