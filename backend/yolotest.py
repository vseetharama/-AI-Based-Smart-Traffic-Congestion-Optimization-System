# =========================================================
# AI Traffic System - YOLO Vehicle Detection + Data Storage
# =========================================================

import cv2

_shared_yolo_model = None


def load_yolo_model(model_path="yolov8n.pt"):
    """
    Lazily load and reuse the YOLO model.
    The same model instance is cached and returned on subsequent calls.
    """
    global _shared_yolo_model
    if _shared_yolo_model is None:
        from ultralytics import YOLO
        _shared_yolo_model = YOLO(model_path)
    return _shared_yolo_model


def detect_vehicles(frame, model=None):
    """
    Run YOLO inference on a single frame and return vehicle metrics.

    Returns:
      - vehicle_count: number of vehicles detected
      - detections: list of detected vehicle bounding boxes and classes
      - processed_frame: the input frame annotated with boxes and count text
    """
    if model is None:
        model = load_yolo_model()

    results = model(frame, verbose=False)
    vehicle_count = 0
    detections = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])  # class id

            # COCO vehicle classes:
            # 2=car, 3=motorcycle, 5=bus, 7=truck
            if cls in [2, 3, 5, 7]:
                vehicle_count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    "class_id": cls,
                    "bbox": [x1, y1, x2, y2],
                })
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.putText(
        frame,
        f"Vehicles: {vehicle_count}",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    return vehicle_count, detections, frame


def process_video(input_path, output_path="output.mp4", data_path="vehicle_data.txt", max_frames=300):
    """
    Process the video at `input_path` using the existing YOLO detection
    and counting logic. Saves annotated video to `output_path` and
    frame-wise counts to `data_path`.

    Parameters:
    - input_path: path to the input video file to process
    - output_path: destination path for annotated output video
    - data_path: destination path for CSV with frame counts
    - max_frames: maximum number of frames to process (default 300)

    NOTE: This function preserves the original detection/counting logic
    exactly as in the original script. It is synchronous and will block
    until processing completes.
    """

    # -------------------------------
    # Lazily load and reuse the YOLO model.
    # -------------------------------
    model = load_yolo_model()

    # -------------------------------
    # 2. Load Input Video (now from parameter)
    # -------------------------------
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        print(f"❌ Error: Cannot open video at {input_path}")
        return False


# -------------------------------
# 3. Get Video Properties
# -------------------------------
# Get video properties
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = int(cap.get(5))

    # -------------------------------
    # 4. Setup Output Video Writer
    # -------------------------------
    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (width, height)
    )

    # -------------------------------
    # 5. Create Data File
    # -------------------------------
    # This will store frame-wise vehicle count
    file = open(data_path, "w")
    file.write("Frame,VehicleCount\n")   # Header


# -------------------------------
# 6. Frame Control
# -------------------------------
    frame_count = 0
    MAX_FRAMES = max_frames   # limit processing (~10 sec)

    # -------------------------------
    # 7. Process Video Frames
    # -------------------------------
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        # Stop after max frames
        if frame_count > MAX_FRAMES:
            break

        print(f"Processing frame: {frame_count}")

        # -------------------------------
        # 8. YOLO Detection
        # -------------------------------
        vehicle_count, detections, frame = detect_vehicles(frame, model=model)

        # -------------------------------
        # 10. Display Count on Frame
        # -------------------------------
        cv2.putText(
            frame,
            f"Vehicles: {vehicle_count}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # -------------------------------
        # 11. Save Data to File
        # -------------------------------
        file.write(f"{frame_count},{vehicle_count}\n")

        # -------------------------------
        # 12. Save Frame to Output Video
        # -------------------------------
        out.write(frame)

    # -------------------------------
    # 13. Release Resources
    # -------------------------------
    cap.release()
    out.release()
    file.close()

    print("✅ Processing complete!")
    print(f"📁 Output video: {output_path}")
    print(f"📊 Data file: {data_path}")

    return True


if __name__ == "__main__":
    # Maintain original behavior when running this script directly
    process_video("videos/road1.mp4")