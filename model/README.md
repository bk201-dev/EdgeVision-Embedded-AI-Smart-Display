# AI Model

The vision component of EdgeVision is based on a custom convolutional neural network trained to classify cropped face images into the two visual categories used by the prototype.

The classifier is only one part of the complete system: its output is later used by the embedded application to select the content displayed to the user.

---

## Pipeline

```text
Camera Frame
      ↓
Face Detection
      ↓
Face Crop
      ↓
Resize to 96 × 96
      ↓
Normalization
      ↓
Custom CNN
      ↓
Class + Confidence
