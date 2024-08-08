from .packages.ultralytics import YL


def train(version):
    v = version
    model = YL(f"/data/lizr/TSLZ/models/yolov8{version}-seg.yaml").load(f"/data/lizr/TSLZ/models/yolov8{v}-seg.pt")
    results = model.train(data="/data/lizr/TSLZ/data/dataMy.yaml",
                          epochs=100, imgsz=1600, batch=-1, device=7,
                          project="/data/lizr/TSLZ/runs/", name=f"v8{v}TS-train", exist_ok=True,
                          task="segment", amp=True, close_mosaic=10, patience=10)


if __name__ == "__main__":
    train("s")
