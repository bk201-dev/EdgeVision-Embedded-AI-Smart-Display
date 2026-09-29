# Hardware

The hardware side of **EdgeVision** is intentionally compact.

An **ESP32-CAM** handles image acquisition, Wi-Fi communication and display control, while a **3.5-inch TFT** presents the dynamically selected content.

---

## Hardware Architecture

```mermaid
flowchart LR
    CAM["ESP32-CAM<br/>Image Capture"]
    WIFI["Wi-Fi / HTTP"]
    AI["AI Server<br/>Flask + TensorFlow"]
    LOGIC["ESP32-CAM<br/>Content Selection"]
    TFT["3.5-inch TFT<br/>Display"]

    CAM -->|JPEG| WIFI
    WIFI --> AI
    AI -->|Class + Confidence| LOGIC
    LOGIC --> TFT
```

---

## Hardware Roles

| Hardware | Role |
|---|---|
| **ESP32-CAM** | Image capture, JPEG transmission, Wi-Fi communication and embedded control |
| **3.5-inch TFT** | Displays the selected advertisement or visual content |
| **AI Server** | Runs face detection and CNN inference |

---

## System Flow

```mermaid
flowchart TD
    A["Capture Image"] --> B["Send JPEG"]
    B --> C["AI Inference"]
    C --> D["Receive Classification"]
    D --> E["Select Content"]
    E --> F["Update TFT"]
    F --> A
```

The ESP32-CAM remains lightweight: it captures images and controls the physical interface, while the computationally expensive neural-network inference is executed remotely.

---

## Communication

### ESP32-CAM → AI Server

```text
HTTP POST /predict
Content-Type: image/jpeg
```

The camera frame is compressed as JPEG and sent over Wi-Fi.

### AI Server → ESP32-CAM

Example response:

```json
{
  "label": "woman",
  "confidence": 0.9632,
  "confidence_percent": 96.32
}
```

The ESP32-CAM uses the returned result to determine which content should be shown on the TFT.

---

## Hardware Files

```text
hardware/
├── README.md
├── system_architecture.md
├── wiring.md
└── bom.csv
```

---

## Design Idea

```mermaid
flowchart LR
    A["SEE<br/>ESP32-CAM"]
    B["UNDERSTAND<br/>AI Server"]
    C["DECIDE<br/>ESP32 Logic"]
    D["ACT<br/>TFT Display"]

    A --> B --> C --> D
```

EdgeVision connects computer vision to a physical output rather than stopping at an AI prediction.
