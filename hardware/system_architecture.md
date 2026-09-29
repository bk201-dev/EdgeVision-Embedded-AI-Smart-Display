# System Architecture

EdgeVision is split into two main parts:

- the **embedded side**, based on the ESP32-CAM and TFT display,
- the **AI side**, running face detection and CNN inference on a separate machine.

---

## High-Level Architecture

```mermaid
flowchart LR

    CAM["ESP32-CAM<br/>Image Capture"]

    WIFI["Wi-Fi<br/>HTTP"]

    SERVER["AI Server<br/>Flask + TensorFlow"]

    AI["Face Detection<br/>CNN Inference"]

    LOGIC["ESP32-CAM<br/>Content Logic"]

    TFT["3.5-inch TFT<br/>ILI9486<br/>480 × 320"]

    CAM -->|JPEG Image| WIFI
    WIFI --> SERVER
    SERVER --> AI
    AI -->|Label + Confidence| LOGIC
    LOGIC --> TFT
```

---

## System Flow

```mermaid
flowchart TD

    A["Capture Camera Frame"]
    B["Compress as JPEG"]
    C["Send HTTP POST"]
    D["Detect Face"]
    E["Resize to 96 × 96"]
    F["CNN Inference"]
    G["Return Classification"]
    H["Select Display Content"]
    I["Update TFT"]

    A --> B --> C --> D --> E --> F --> G --> H --> I
```

---

## Embedded Side

The **ESP32-CAM** is responsible for:

- image acquisition,
- JPEG generation,
- Wi-Fi communication,
- sending images to the AI server,
- receiving the classification result,
- selecting the corresponding content,
- controlling the display.

---

## AI Side

The AI server is responsible for:

```mermaid
flowchart LR

    A["JPEG Image"]
    B["Face Detection"]
    C["Face Crop"]
    D["Resize + Normalize"]
    E["CNN"]
    F["Label + Confidence"]

    A --> B --> C --> D --> E --> F
```

The inference server exposes:

```text
POST /predict
```

Example response:

```json
{
  "label": "woman",
  "confidence": 0.9632,
  "confidence_percent": 96.32
}
```

---

## Display

The display used in the prototype is:

| Property | Value |
|---|---|
| Size | 3.5 inch |
| Resolution | 480 × 320 |
| Controller | ILI9486 |
| Interface | 16-bit parallel |
| Supply | 3.3 – 5.5 V |
| Touch | Yes |

The TFT displays the content selected after the AI result is received.

---

## Communication Architecture

```mermaid
sequenceDiagram

    participant ESP as ESP32-CAM
    participant AI as AI Server
    participant TFT as TFT Display

    ESP->>AI: JPEG image via HTTP POST
    AI->>AI: Face detection
    AI->>AI: CNN inference
    AI-->>ESP: Label + confidence
    ESP->>ESP: Select content
    ESP->>TFT: Update display
```

---

## Design Separation

```mermaid
flowchart LR

    A["SEE<br/>ESP32-CAM"]
    B["UNDERSTAND<br/>AI Server"]
    C["DECIDE<br/>ESP32 Logic"]
    D["ACT<br/>ILI9486 TFT"]

    A --> B --> C --> D
```

The main design idea is to keep the embedded hardware lightweight while moving the computationally expensive neural-network inference to a more capable machine.

---

## Hardware Constraint

The ESP32-CAM already uses many GPIO pins for the camera interface.

The selected ILI9486 display uses a **16-bit parallel bus**, which also requires a large number of GPIOs.

For this reason, the final ESP32-CAM ↔ TFT pin mapping should only be documented after the interface has been physically validated.
