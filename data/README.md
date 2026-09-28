# Dataset

Do not commit a large dataset directly to this repository.

Document:

- dataset name,
- source / license,
- download instructions,
- class labels,
- preprocessing,
- folder structure.

Recommended local structure:

```text
data/
├── raw/
├── processed/
└── README.md
```

The `.gitignore` excludes `data/raw/` and `data/processed/`.
