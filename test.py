from ultralytics import YOLO

model = YOLO("model/best.pt")

results = model.predict(
    source="test.png",
    project="runs",
    name="predict"
)