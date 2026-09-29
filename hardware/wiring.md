# Hardware Wiring

## Main Hardware

```mermaid
flowchart LR
    CAM["ESP32-CAM<br/>Camera + Wi-Fi"]
    TFT["ILI9486 TFT<br/>3.5 inch - 480 × 320"]
    POWER["Regulated Power<br/>5 V"]

    POWER --> CAM
    POWER --> TFT
    CAM --> TFT
