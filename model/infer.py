"""
EdgeVision Ads - inference entry point.

Replace the placeholder classifier with the real model used by the project.
"""

import cv2


def classify_frame(frame):
    # TODO:
    # 1. detect / crop region of interest
    # 2. resize and normalize
    # 3. run model inference
    # 4. return label and confidence
    return "unknown", 0.0


def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera")

    while True:
        ok, frame = camera.read()
        if not ok:
            break

        label, confidence = classify_frame(frame)

        cv2.putText(
            frame,
            f"{label}: {confidence:.2f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

        cv2.imshow("EdgeVision Ads", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
