from pathlib import Path
import random

import cv2
import matplotlib.pyplot as plt
import numpy as np

from sklearn.model_selection import train_test_split

from tensorflow.keras import backend as K
from tensorflow.keras.layers import (
    Input,
    BatchNormalization,
    Conv2D,
    MaxPooling2D,
    Activation,
    Flatten,
    Dropout,
    Dense
)
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import (
    ImageDataGenerator,
    img_to_array
)
from tensorflow.keras.utils import to_categorical


EPOCHS = 100
LEARNING_RATE = 1e-3
BATCH_SIZE = 64
IMG_DIMS = (96, 96, 3)

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR.parent / "data" / "gender_dataset_face"

MODEL_PATH = BASE_DIR / "gender_detection.weights.h5"
PLOT_PATH = BASE_DIR / "training_plot.png"

SEED = 42

random.seed(SEED)
np.random.seed(SEED)


def load_dataset():
    data = []
    labels = []

    image_files = [
        path
        for path in DATASET_PATH.rglob("*")
        if path.is_file()
    ]

    random.shuffle(image_files)

    for image_path in image_files:
        image = cv2.imread(str(image_path))

        if image is None:
            continue

        image = cv2.resize(
            image,
            (IMG_DIMS[0], IMG_DIMS[1])
        )

        image = img_to_array(image)

        label_name = image_path.parent.name.lower()

        if label_name == "woman":
            label = 1
        elif label_name == "man":
            label = 0
        else:
            continue

        data.append(image)
        labels.append(label)

    data = np.array(
        data,
        dtype="float32"
    ) / 255.0

    labels = np.array(labels)

    return data, labels


def build_model(
    width,
    height,
    depth,
    classes
):
    channel_dim = -1

    if K.image_data_format() == "channels_first":
        input_shape = (
            depth,
            height,
            width
        )
        channel_dim = 1
    else:
        input_shape = (
            height,
            width,
            depth
        )

    model = Sequential([
        Input(shape=input_shape),

        Conv2D(
            32,
            (3, 3),
            padding="same"
        ),
        Activation("relu"),
        BatchNormalization(axis=channel_dim),
        MaxPooling2D(pool_size=(3, 3)),
        Dropout(0.25),

        Conv2D(
            64,
            (3, 3),
            padding="same"
        ),
        Activation("relu"),
        BatchNormalization(axis=channel_dim),

        Conv2D(
            64,
            (3, 3),
            padding="same"
        ),
        Activation("relu"),
        BatchNormalization(axis=channel_dim),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        Conv2D(
            128,
            (3, 3),
            padding="same"
        ),
        Activation("relu"),
        BatchNormalization(axis=channel_dim),

        Conv2D(
            128,
            (3, 3),
            padding="same"
        ),
        Activation("relu"),
        BatchNormalization(axis=channel_dim),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        Flatten(),

        Dense(1024),
        Activation("relu"),
        BatchNormalization(),
        Dropout(0.5),

        Dense(classes),
        Activation("sigmoid")
    ])

    return model


def main():
    print(f"Dataset: {DATASET_PATH}")

    data, labels = load_dataset()

    if len(data) == 0:
        raise RuntimeError(
            f"No valid images found in {DATASET_PATH}"
        )

    trainX, valX, trainY, valY = train_test_split(
        data,
        labels,
        test_size=0.2,
        random_state=SEED,
        stratify=labels
    )

    trainY = to_categorical(
        trainY,
        num_classes=2
    )

    valY = to_categorical(
        valY,
        num_classes=2
    )

    augmentation = ImageDataGenerator(
        rotation_range=25,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest"
    )

    model = build_model(
        width=IMG_DIMS[0],
        height=IMG_DIMS[1],
        depth=IMG_DIMS[2],
        classes=2
    )

    optimizer = Adam(
        learning_rate=LEARNING_RATE
    )

    model.compile(
        loss="binary_crossentropy",
        optimizer=optimizer,
        metrics=["accuracy"]
    )

    history = model.fit(
        augmentation.flow(
            trainX,
            trainY,
            batch_size=BATCH_SIZE
        ),
        validation_data=(
            valX,
            valY
        ),
        steps_per_epoch=max(
            1,
            len(trainX) // BATCH_SIZE
        ),
        epochs=EPOCHS,
        verbose=1
    )

    model.save_weights(
        MODEL_PATH
    )

    plt.figure()

    epochs_range = np.arange(
        len(history.history["loss"])
    )

    plt.plot(
        epochs_range,
        history.history["loss"],
        label="train_loss"
    )

    plt.plot(
        epochs_range,
        history.history["val_loss"],
        label="val_loss"
    )

    plt.plot(
        epochs_range,
        history.history["accuracy"],
        label="train_accuracy"
    )

    plt.plot(
        epochs_range,
        history.history["val_accuracy"],
        label="val_accuracy"
    )

    plt.title(
        "Training Loss and Accuracy"
    )

    plt.xlabel("Epoch")
    plt.ylabel("Loss / Accuracy")

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        PLOT_PATH,
        dpi=200
    )

    plt.close()

    print(
        f"Model weights saved to: {MODEL_PATH}"
    )

    print(
        f"Training plot saved to: {PLOT_PATH}"
    )


if __name__ == "__main__":
    main()