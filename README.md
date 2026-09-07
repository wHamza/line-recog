# Underwater Line Recognition

A computer-vision and vehicle-control prototype for detecting a pipe-defined underwater route and using the result in an autonomous vehicle workflow.

## Stack

- Python and OpenCV
- Ultralytics YOLO
- PyMAVLink
- Custom vehicle-control helpers

## Repository structure

- `main/detection.py` — detection utilities
- `main/Vehicleorgi.py` — vehicle-control abstraction
- `main/main.py` — movement experiment
- `main/Untitled.ipynb` — notebook experiments
- `main/*.pt` — model checkpoints

## Status

Research prototype. The scripts include hardware-specific serial settings and must be reviewed before connecting to a real vehicle. Test first in a simulator or controlled environment.
