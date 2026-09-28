# AI Vision Model

The perception layer of **EdgeVision** uses a custom TensorFlow/Keras CNN to classify detected face images into the two visual categories used by the prototype.

The model works with `96 × 96` images and is shared by both the local webcam demo and the network inference server.

---

## Vision Pipeline

```mermaid
flowchart LR
    A[Camera Frame] --> B[Face Detection]
    B --> C[Face Crop]
    C --> D[Resize 96 × 96]
    D --> E[Normalize / 255]
    E --> F[Custom CNN]
    F --> G[Class + Confidence]
```

### Input

| Parameter | Value |
|---|---|
| Resolution | 96 × 96 |
| Channels | 3 |
| Color order | BGR |
| Normalization | `/255.0` |
| Classes | `man`, `woman` |

Training and inference use the same OpenCV-based preprocessing pipeline.

---

## CNN Architecture

```mermaid
flowchart TD
    A["Input<br/>96 × 96 × 3"]

    B["Conv2D 32<br/>ReLU + BatchNorm"]
    C["MaxPool + Dropout"]

    D["Conv2D 64 × 2<br/>ReLU + BatchNorm"]
    E["MaxPool + Dropout"]

    F["Conv2D 128 × 2<br/>ReLU + BatchNorm"]
    G["MaxPool + Dropout"]

    H["Flatten"]
    I["Dense 1024<br/>ReLU + BatchNorm"]
    J["Dropout 0.5"]

    K["Dense 2<br/>Sigmoid"]
    L["Classification"]

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J --> K --> L
```

---

## Training

| Parameter | Value |
|---|---:|
| Epochs | 100 |
| Batch size | 64 |
| Learning rate | 0.001 |
| Optimizer | Adam |
| Validation split | 20% |
| Loss | Binary Cross-Entropy |

Data augmentation includes rotation, translation, shear, zoom and horizontal flipping.

### Training Results

<p align="center">
  <img src="training_plot.png" width="700">
</p>

The model reaches high training and validation accuracy, although the validation-loss curve contains occasional spikes that deserve further evaluation with metrics such as a confusion matrix, precision, recall and F1-score.

---

## Local Webcam Inference

[`webcam_inference.py`](webcam_inference.py)

```mermaid
flowchart LR
    A[PC Webcam] --> B[Face Detection]
    B --> C[Preprocessing]
    C --> D[CNN]
    D --> E[Label + Confidence]
    E --> F[Live Overlay]
```

This mode is mainly used for quick local testing of the complete vision pipeline.

---

## Embedded / Network Inference

[`server_inference.py`](server_inference.py)

```mermaid
flowchart LR
    A[Embedded Camera]
    B[JPEG Image]
    C[Flask AI Server]
    D[Face Detection]
    E[CNN Inference]
    F[JSON Response]
    G[Content Logic]

    A --> B
    B -->|HTTP POST| C
    C --> D --> E --> F
    F --> G
```

The server exposes:

```text
POST /predict
```

Example response:

```json
{
  "label": "woman",
  "prob": 0.9632,
  "confidence_percent": 96.32
}
```

---

## Why Use an AI Server?

The trained model is approximately **100 MB**, making it too heavy for a small embedded camera/controller.

EdgeVision therefore separates the workload:

```mermaid
flowchart LR
    A["Embedded Device<br/>Capture + JPEG + Wi-Fi"]
    B["AI Server<br/>Face Detection + TensorFlow"]
    C["Embedded Application<br/>Content Selection"]

    A -->|Image| B
    B -->|Classification| C
```

This keeps the embedded hardware lightweight while the more computationally expensive inference runs on a capable machine.

---

## Model Files

```text
model/
├── train.py
├── webcam_inference.py
├── server_inference.py
├── training_plot.png
└── README.md
```

The trained `gender_detection.model` file is not stored directly in the repository because of its size.

---

## Limitations

The classifier predicts only the visual categories present in its training dataset and can be affected by lighting, pose, image quality, occlusion and dataset bias.

It should not be interpreted as determining a person's actual gender identity. In EdgeVision, it is used only as a computer-vision component inside an embedded-AI prototype.

---

## Role Inside EdgeVision

```mermaid
flowchart LR
    A[SEE<br/>Camera]
    B[UNDERSTAND<br/>AI Model]
    C[DECIDE<br/>Content Logic]
    D[ACT<br/>Smart Display]

    A --> B --> C --> D
```

The model provides the **perception layer** that connects the camera to the rest of the embedded system.
