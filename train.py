from ultralytics import YOLO

# Load base YOLO model
model = YOLO("yolov8n.pt")  # lightweight model

# Train model on your dataset
model.train(
    data="dataset/data.yaml",   # IMPORTANT
    epochs=20,
    imgsz=640
)