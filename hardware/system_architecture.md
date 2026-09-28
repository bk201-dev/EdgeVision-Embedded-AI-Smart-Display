# System Architecture

## Functional Architecture

```mermaid
flowchart LR
    CAM["Camera"] --> AI["AI Inference"]
    AI --> LINK["Communication Link"]
    LINK --> MCU["Embedded Controller"]
    MCU --> DISP["Display"]
```

## Design Notes

Fill these with your actual implementation:

- **Camera:** TODO
- **Inference hardware:** TODO
- **Embedded controller:** TODO
- **Display:** TODO
- **Communication interface:** TODO
- **Power input:** TODO

## Data Flow

```text
Image
  ↓
Preprocessing
  ↓
Classification
  ↓
Confidence Check
  ↓
Content ID
  ↓
MCU
  ↓
Display
```
