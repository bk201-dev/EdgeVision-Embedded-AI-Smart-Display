# AI Model

This folder contains the training and inference side of EdgeVision Ads.

## Expected contents

- `train.py` — training entry point
- `infer.py` — local inference entry point
- `config.example.json` — example configuration
- exported model file — add only if its size is reasonable

## Document before publishing

1. Dataset source
2. Training labels
3. Train / validation / test split
4. Input image size
5. Model architecture
6. Preprocessing
7. Metrics
8. Confidence threshold
9. Known failure cases
10. Export format used by the embedded / edge target

Do not describe the classifier as determining a person's definitive gender. Describe the model according to the labels and data it was actually trained on.
