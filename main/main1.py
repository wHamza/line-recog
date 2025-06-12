import cv2
import numpy as np
import time
from ultralytics import YOLO
from detection import CONFIG, preprocess, draw_boxes, get_command, is_similar_shape
from Vehicleorgi import Vehicle
from pymavlink import mavutil

SIMULATION_MODE = False
SHOW_WINDOW = False
ENABLE_CANNY = False  # Toggle to disable second model for testing


def main():
    sub = None
    if not SIMULATION_MODE:
        sub = Vehicle('COM9', _baud=9600)
        sub.vehicle.wait_heartbeat()
        sub.arm_vehicle()
        sub.set_mod_vehicle()

    model_canny = YOLO(CONFIG["model_canny_path"])
    model_normal = YOLO(CONFIG["model_normal_path"])
    model_canny.to("cuda") if ENABLE_CANNY else None
    model_normal.to("cuda")

    cap = cv2.VideoCapture(CONFIG["video_path"])
    if not cap.isOpened():
        exit("Video açılamadı")

    seen_anomalies = set()
    frame_count, start_time = 0, time.time()
    last_command_time = 0
    command_interval = 0.5

    print("Starting navigation loop...")
    try:
        while True:
            loop_start = time.time()
            ret, frame = cap.read()
            if not ret:
                print("End of video stream or error reading frame.")
                break

            # Timing for performance debugging
            t0 = time.time()

            if ENABLE_CANNY:
                canny_img = preprocess(frame)
                t1 = time.time()
                res_canny = model_canny.predict(canny_img, imgsz=640, conf=CONFIG["confidence_threshold"], verbose=False)
                t2 = time.time()
            else:
                res_canny = []
                t1 = t2 = time.time()

            res_normal = model_normal.predict(frame, imgsz=640, conf=CONFIG["confidence_threshold"], iou=0.4, verbose=False)
            t3 = time.time()

            cmd = get_command(res_canny, frame.shape[1], frame) if ENABLE_CANNY else "duz git"
            anomalies_now = set()
            active_anomaly = False

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

            if cmd == "":
                anomalies_now.add("yol yok")

            active_anomaly = bool(anomalies_now)
            now = time.time()

            if now - last_command_time >= command_interval:
                if not SIMULATION_MODE:
                    if active_anomaly:
                        sub.dur()
                        print(f"ANOMALY DETECTED: {', '.join(sorted(anomalies_now))}. Vehicle stopped.")
                    else:
                        if cmd == "duz git":
                            print("COMMAND: Move Forward")
                            sub.move_forward(duration=0.1)
                        elif cmd == "sola don":
                            print("COMMAND: Turn Left")
                            sub.move_left(duration=0.1)
                        elif cmd == "saga don":
                            print("COMMAND: Turn Right")
                            sub.move_right(duration=0.1)
                        elif cmd == "yol yok":
                            print("COMMAND: No path detected. Stopping.")
                            sub.dur()
                        else:
                            print(f"UNKNOWN COMMAND: {cmd}. Stopping.")
                            sub.dur()
                last_command_time = now

            draw_boxes(frame, res_canny, model_canny.names if ENABLE_CANNY else {}, (0, 255, 0), "Canny: ")
            draw_boxes(frame, res_normal, model_normal.names, (255, 0, 0), "Normal: ")
            cv2.putText(frame, f"KOMUT: {cmd}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Anomaliler: {', '.join(sorted(seen_anomalies))}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(frame, "ANOMAL\u0130 AKT\u0130F" if active_anomaly else "NORMAL", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255) if active_anomaly else (0, 255, 0), 2)

            if CONFIG["show_fps"]:
                frame_count += 1
                if time.time() - start_time >= 1:
                    fps = frame_count / (time.time() - start_time)
                    cv2.putText(frame, f"FPS: {fps:.2f}", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    frame_count, start_time = 0, time.time()

            if SHOW_WINDOW:
                cv2.imshow(CONFIG["win"], frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            print(f"Frame: {1000*(time.time() - loop_start):.1f} ms | Preproc: {1000*(t1-t0):.1f} | Canny YOLO: {1000*(t2-t1):.1f} | Normal YOLO: {1000*(t3-t2):.1f}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Releasing resources...")
        if not SIMULATION_MODE:
            sub.dur()
        cap.release()
        if SHOW_WINDOW:
            cv2.destroyAllWindows()
        print("Integration finished.")


if __name__ == "__main__":
    main()
