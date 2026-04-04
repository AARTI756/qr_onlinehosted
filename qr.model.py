from ultralytics import YOLO
import cv2

# Load trained model
model = YOLO("runs/detect/train/weights/best.pt")

def detect_qr(image_path):
    img = cv2.imread(image_path)
    results = model(img)

    boxes = []

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            boxes.append((x1, y1, x2, y2))

            cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)

    return img, boxes