from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Input,
    Conv2D,
    MaxPooling2D,
    Activation,
    Flatten,
    Dropout,
    Dense,
    BatchNormalization
)
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras import backend as K

import numpy as np
import cv2
import cvlib as cv


MODEL_PATH = "gender_detection.h5"

CLASSES = [
    "man",
    "woman"
]


def build_model(
    width=96,
    height=96,
    depth=3,
    classes=2
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

    model = Sequential()

    model.add(
        Input(
            shape=input_shape
        )
    )

    model.add(
        Conv2D(
            32,
            (3, 3),
            padding="same"
        )
    )

    model.add(
        Activation("relu")
    )

    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )

    model.add(
        MaxPooling2D(
            pool_size=(3, 3)
        )
    )

    model.add(
        Dropout(0.25)
    )


    model.add(
        Conv2D(
            64,
            (3, 3),
            padding="same"
        )
    )

    model.add(
        Activation("relu")
    )

    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )


    model.add(
        Conv2D(
            64,
            (3, 3),
            padding="same"
        )
    )

    model.add(
        Activation("relu")
    )

    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )

    model.add(
        MaxPooling2D(
            pool_size=(2, 2)
        )
    )

    model.add(
        Dropout(0.25)
    )


    model.add(
        Conv2D(
            128,
            (3, 3),
            padding="same"
        )
    )

    model.add(
        Activation("relu")
    )

    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )


    model.add(
        Conv2D(
            128,
            (3, 3),
            padding="same"
        )
    )

    model.add(
        Activation("relu")
    )

    model.add(
        BatchNormalization(
            axis=channel_dim
        )
    )

    model.add(
        MaxPooling2D(
            pool_size=(2, 2)
        )
    )

    model.add(
        Dropout(0.25)
    )


    model.add(
        Flatten()
    )

    model.add(
        Dense(1024)
    )

    model.add(
        Activation("relu")
    )

    model.add(
        BatchNormalization()
    )

    model.add(
        Dropout(0.5)
    )


    model.add(
        Dense(classes)
    )

    model.add(
        Activation("sigmoid")
    )

    return model


model = build_model()

model.load_weights(
    MODEL_PATH
)


webcam = cv2.VideoCapture(0)


while webcam.isOpened():

    status, frame = webcam.read()

    if not status:
        break


    faces, _ = cv.detect_face(
        frame
    )


    for face in faces:

        startX, startY = (
            face[0],
            face[1]
        )

        endX, endY = (
            face[2],
            face[3]
        )


        height, width = frame.shape[:2]

        startX = max(
            0,
            startX
        )

        startY = max(
            0,
            startY
        )

        endX = min(
            width,
            endX
        )

        endY = min(
            height,
            endY
        )


        face_crop = np.copy(
            frame[
                startY:endY,
                startX:endX
            ]
        )


        if (
            face_crop.shape[0] < 10
            or
            face_crop.shape[1] < 10
        ):
            continue


        face_crop = cv2.resize(
            face_crop,
            (96, 96)
        )

        face_crop = (
            face_crop.astype(
                "float32"
            )
            / 255.0
        )

        face_crop = img_to_array(
            face_crop
        )

        face_crop = np.expand_dims(
            face_crop,
            axis=0
        )


        prediction = model.predict(
            face_crop,
            verbose=0
        )[0]


        class_index = int(
            np.argmax(
                prediction
            )
        )


        confidence = float(
            prediction[
                class_index
            ]
        )


        label = (
            f"{CLASSES[class_index]}: "
            f"{confidence * 100:.2f}%"
        )


        cv2.rectangle(
            frame,
            (startX, startY),
            (endX, endY),
            (0, 255, 0),
            2
        )


        label_y = (
            startY - 10
            if startY > 20
            else startY + 20
        )


        cv2.putText(
            frame,
            label,
            (startX, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


    cv2.imshow(
        "EdgeVision - Webcam Inference",
        frame
    )


    if (
        cv2.waitKey(1) & 0xFF
        == ord("q")
    ):
        break


webcam.release()

cv2.destroyAllWindows()