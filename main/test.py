from ultralytics import YOLO
import cv2, time

model = YOLO('yolov8n.pt')  # lightweight for speed
cap = cv2.VideoCapture('yeni12.mp4')

count, t0 = 0, time.time()
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    results = model.predict(frame, imgsz=640, verbose=False)
    count += 1
    if time.time() - t0 > 30:  # run for 3 seconds
        print(f"FPS: {count / (time.time() - t0):.2f}")
        break
cap.release()