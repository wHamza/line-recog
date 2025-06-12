import cv2, numpy as np, time
from ultralytics import YOLO

CONFIG = {
    "video_path": "yeni12.mp4",
    "model_canny_path": "yol.pt",
    "model_normal_path": "newKt.pt",
    "confidence_threshold": 0.45,
    "line_class": "yol",
    "offset_thresh": 40,
    "canny_thresh": (50, 150),
    "blur_kernel": (5, 5),
    "show_fps": True,
    "debug": True,
    "win": "Navigation",
    "anomalies": ["circle", "triangle", "rectangle", "square", "deltoid"],
    "delay": (1, 500)
}

model_canny = YOLO(CONFIG["model_canny_path"])
model_normal = YOLO(CONFIG["model_normal_path"])
cap = cv2.VideoCapture(CONFIG["video_path"])
if not cap.isOpened(): exit("Video açılamadı")

seen_anomalies = set()
frame_count, start_time = 0, time.time()

def preprocess(frame):  # Canny edge + 3-channel convert
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, CONFIG["blur_kernel"], 0)
    canny = cv2.Canny(blur, *CONFIG["canny_thresh"])
    return cv2.merge([canny]*3)

def draw_boxes(frame, results, names, color, label_prefix=""):
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls, conf = int(box.cls[0]), float(box.conf[0])
            name = names.get(cls, f"cls_{cls}")
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label_prefix}{name} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.circle(frame, ((x1+x2)//2, (y1+y2)//2), 4, (0,0,255), -1)

def is_similar_shape(a, b):
    return {"square", "rectangle"} == {a, b}

def get_command(canny_results, w, frame=None):
    centers = []
    for r in canny_results:
        for box in r.boxes:
            if model_canny.names[int(box.cls[0])] == CONFIG["line_class"]:
                x1, x2 = map(int, (box.xyxy[0][0], box.xyxy[0][2]))
                centers.append((x1+x2)//2)
    if not centers:
        #seen_anomalies.add("")
        return ""
    avg_cx = int(np.mean(centers))
    offset = avg_cx - w//2
    if CONFIG["debug"] and frame is not None:
        h = frame.shape[0]
        cv2.line(frame, (avg_cx, h-50), (avg_cx, h), (255,255,0), 2)
        cv2.line(frame, (w//2, h-50), (w//2, h), (0,255,255), 2)
    return "duz git" if abs(offset) < CONFIG["offset_thresh"] else ("sola don" if offset < 0 else "saga don")

while True:
    ret, frame = cap.read()
    if not ret: break
    canny_img = preprocess(frame)
    res_canny = model_canny.predict(canny_img, imgsz=640, conf=CONFIG["confidence_threshold"], verbose=False)
    res_normal = model_normal.predict(frame, imgsz=640, conf=CONFIG["confidence_threshold"], iou=0.4, verbose=False)
    
    cmd = get_command(res_canny, frame.shape[1], frame)
    anomalies_now, active = set(), False

    # Geometrik anomali kontrolü
    existing_shapes = set()
    for r in res_normal:
        for box in r.boxes:
            cls = int(box.cls[0])
            name = model_normal.names.get(cls)
            conf = box.conf[0]
            if name in CONFIG["anomalies"] and conf > 0.75:
                if any(is_similar_shape(name, s) for s in existing_shapes):
                    continue
                existing_shapes.add(name)
                anomalies_now.add(name)
                seen_anomalies.add(name)

    if cmd == "": anomalies_now.add("yol yok")
    active = bool(anomalies_now)

    draw_boxes(frame, res_canny, model_canny.names, (0,255,0), "Canny: ")
    draw_boxes(frame, res_normal, model_normal.names, (255,0,0), "Normal: ")
    cv2.putText(frame, f"KOMUT: {cmd}", (20,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv2.putText(frame, f"Anomaliler: {', '.join(sorted(seen_anomalies))}", (20,110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
    cv2.putText(frame, "ANOMALİ AKTİF" if active else "NORMAL", (20,70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255) if active else (0,255,0), 2)

    if CONFIG["show_fps"]:
        frame_count += 1
        if time.time() - start_time >= 1:
            fps = frame_count / (time.time() - start_time)
            cv2.putText(frame, f"FPS: {fps:.2f}", (20,150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)
            frame_count, start_time = 0, time.time()
    
    cv2.imshow(CONFIG["win"], frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
