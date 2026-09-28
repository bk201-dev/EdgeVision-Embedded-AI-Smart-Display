# Embedded System

This folder documents the embedded side of EdgeVision Ads.

The embedded controller is responsible for receiving the classification result or content ID and controlling the display / local hardware.

## Recommended documentation

- MCU / board used
- communication interface
- packet format
- display driver
- power requirements
- state machine
- error handling

## Example message flow

```text
AI Processor
   │
   │  content_id
   ▼
Embedded Controller
   │
   ▼
Display Driver
   │
   ▼
Selected Content
```
